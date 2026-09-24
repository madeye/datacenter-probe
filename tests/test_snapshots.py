import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("snapshots", Path(__file__).resolve().parents[1] / "scripts/build_snapshots.py")
snapshots = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(snapshots)


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        self.run_git("init", "-b", "main")
        self.run_git("config", "user.name", "Snapshot Test")
        self.run_git("config", "user.email", "snapshot@example.invalid")
        self.docs = self.repo / "docs"
        self.docs.mkdir()
        self.output = Path(self.temp.name) / "site"
        self.page("index.html", "old")
        (self.docs / "probe.js").write_text("old script")
        self.commit("2026-08-01T23:00:00+00:00")  # August 2 in Singapore
        self.page("index.html", "morning")
        self.page("guian/index.html", "city morning")
        self.commit("2026-08-03T01:00:00+08:00")
        self.page("index.html", "latest")
        self.page("guian/index.html", "city latest")
        (self.docs / "probe.js").write_text("new script")
        self.commit("2026-08-03T22:00:00+08:00")

    def run_git(self, *args, env=None):
        return subprocess.check_output(["git", "-C", str(self.repo), *args], env=env, stderr=subprocess.DEVNULL, text=True)

    def page(self, name, text):
        path = self.docs / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f'<html><head><link rel="canonical" href="{snapshots.SITE}{name}"></head><body>{text}</body></html>')

    def commit(self, timestamp):
        self.run_git("add", "docs")
        self.run_git("-c", "core.hooksPath=/dev/null", "commit", "-m", "Update site", env={**os.environ, "GIT_AUTHOR_DATE": timestamp, "GIT_COMMITTER_DATE": timestamp})

    def test_daily_snapshots_preserve_assets_and_use_singapore_date(self):
        catalog = snapshots.build(self.repo, self.output)
        self.assertEqual(list(catalog), ["2026-08-03", "2026-08-02"])
        self.assertIn("latest", (self.output / "2026-08-03/index.html").read_text())
        self.assertNotIn("morning", (self.output / "2026-08-03/index.html").read_text())
        self.assertEqual((self.output / "2026-08-02/probe.js").read_text(), "old script")
        self.assertEqual((self.output / "2026-08-03/probe.js").read_text(), "new script")
        self.assertEqual(json.loads((self.output / "snapshots.json").read_text())["latest"], "2026-08-03")

    def test_navigation_preserves_city_or_falls_back_to_overview(self):
        snapshots.build(self.repo, self.output)
        city = (self.output / "2026-08-03/guian/index.html").read_text()
        self.assertIn('href="../../2026-08-03/guian/" aria-current="date"', city)
        self.assertIn('href="../../2026-08-02/">2026-08-02 · 总览', city)
        self.assertIn('href="../../snapshot-nav.css"', city)
        self.assertIn(snapshots.SITE + "2026-08-03/guian/index.html", city)
        old = (self.output / "2026-08-02/index.html").read_text()
        self.assertIn('href="../2026-08-03/"', old)

    def test_latest_redirects_keep_deep_links_and_support_no_js(self):
        snapshots.build(self.repo, self.output)
        root = (self.output / "index.html").read_text()
        city = (self.output / "guian/index.html").read_text()
        self.assertIn('location.replace("2026-08-03/" + location.search + location.hash)', root)
        self.assertIn('content="0;url=../2026-08-03/guian/"', city)
        self.assertIn(snapshots.SITE + "2026-08-03/guian/", city)
        self.assertNotIn(snapshots.SITE + "../", city)

    def test_rebuild_preserves_historical_content_and_updates_navigation(self):
        snapshots.build(self.repo, self.output)
        old_asset = (self.output / "2026-08-02/probe.js").read_bytes()
        self.page("index.html", "next day")
        self.commit("2026-08-04T08:00:00+08:00")
        snapshots.build(self.repo, self.output)
        self.assertEqual((self.output / "2026-08-02/probe.js").read_bytes(), old_asset)
        self.assertIn('>old</body>', (self.output / "2026-08-02/index.html").read_text())
        self.assertIn('2026-08-04/"', (self.output / "2026-08-02/index.html").read_text())

    def test_worktree_preview_and_output_guard(self):
        self.page("index.html", "uncommitted preview")
        snapshots.build(self.repo, self.output, worktree=True, date="2026-08-04")
        self.assertIn("uncommitted preview", (self.output / "2026-08-04/index.html").read_text())
        with self.assertRaises(ValueError):
            snapshots.build(self.repo, self.docs)
        with self.assertRaises(ValueError):
            snapshots.build(self.repo, self.docs / "nested")
        unowned = Path(self.temp.name) / "unowned"
        unowned.mkdir()
        with self.assertRaises(ValueError):
            snapshots.build(self.repo, unowned)
        with self.assertRaises(ValueError):
            snapshots.build(self.repo, self.output, date="2026-08-05")

    def test_redirect_preserves_social_metadata(self):
        html = snapshots.redirect("2026-08-03/", "2026-08-03/", '<title>City atlas</title><meta property="og:title" content="City atlas"><meta name="description" content="Survey">')
        self.assertIn("<title>City atlas</title>", html)
        self.assertIn('<meta property="og:title" content="City atlas">', html)
        self.assertIn('<meta name="description" content="Survey">', html)

    def test_non_docs_release_remains_after_later_updates(self):
        env = {**os.environ, "GIT_AUTHOR_DATE": "2026-08-04T08:00:00+08:00", "GIT_COMMITTER_DATE": "2026-08-04T08:00:00+08:00"}
        self.run_git("-c", "core.hooksPath=/dev/null", "commit", "--allow-empty", "-m", "Deploy build update", env=env)
        self.page("index.html", "next update")
        self.commit("2026-08-05T08:00:00+08:00")
        catalog = snapshots.build(self.repo, self.output)
        self.assertIn("2026-08-04", catalog)
        self.assertIn("latest", (self.output / "2026-08-04/index.html").read_text())

    def test_shallow_clone_cannot_silently_drop_history(self):
        clone = Path(self.temp.name) / "shallow"
        subprocess.run(["git", "clone", "--depth=1", self.repo.as_uri(), str(clone)], check=True, capture_output=True)
        with self.assertRaisesRegex(ValueError, "full clone"):
            snapshots.build(clone, self.output)


if __name__ == "__main__":
    unittest.main()
