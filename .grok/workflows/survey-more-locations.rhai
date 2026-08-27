let meta = #{
    name: "survey-more-locations",
    description: "Survey additional China datacenter hub cities and add verified campuses to the probe site",
    when_to_use: "When the repo should survey and add more datacenter locations beyond the original five cities",
    phases: [
        #{ title: "Survey", detail: "one scout per candidate hub, OSM + news + Esri tiles" },
        #{ title: "Verify", detail: "one skeptic per city, fail closed" },
        #{ title: "Add", detail: "notes, Esri plates, and pages for confirmed cities" },
    ],
};

let survey_schema = #{
    "type": "object",
    "required": ["slug", "city", "worth_adding", "reason", "origin_lat", "origin_lon", "origin_name", "sites"],
    "properties": #{
        "slug": #{ "type": "string" },
        "city": #{ "type": "string" },
        "worth_adding": #{ "type": "boolean" },
        "reason": #{ "type": "string" },
        "origin_lat": #{ "type": "number" },
        "origin_lon": #{ "type": "number" },
        "origin_name": #{ "type": "string" },
        "region": #{ "type": "string" },
        "sites": #{
            "type": "array",
            "maxItems": 6,
            "items": #{
                "type": "object",
                "required": ["id", "name", "lat", "lon", "confidence", "status", "evidence"],
                "properties": #{
                    "id": #{ "type": "string" },
                    "name": #{ "type": "string" },
                    "lat": #{ "type": "number" },
                    "lon": #{ "type": "number" },
                    "confidence": #{ "type": "string" },
                    "status": #{ "type": "string" },
                    "osm": #{ "type": "string" },
                    "evidence": #{ "type": "string" },
                    "operators": #{ "type": "string" },
                    "exclude": #{ "type": "boolean" },
                },
            },
        },
    },
};

let verdict_schema = #{
    "type": "object",
    "required": ["real", "worth_adding", "reason", "evidence"],
    "properties": #{
        "real": #{ "type": "boolean" },
        "worth_adding": #{ "type": "boolean" },
        "reason": #{ "type": "string" },
        "evidence": #{ "type": "string" },
        "origin_lat": #{ "type": "number" },
        "origin_lon": #{ "type": "number" },
        "origin_name": #{ "type": "string" },
        "confidence": #{ "type": "string" },
    },
};

let add_schema = #{
    "type": "object",
    "required": ["summary", "added"],
    "properties": #{
        "summary": #{ "type": "string" },
        "added": #{
            "type": "array",
            "items": #{ "type": "string" },
        },
        "skipped": #{
            "type": "array",
            "items": #{ "type": "string" },
        },
        "files": #{
            "type": "array",
            "items": #{ "type": "string" },
        },
    },
};

fn trimmed(s) {
    if type_of(s) == "string" {
        s.trim();
        s
    } else {
        ""
    }
}

fn slug_wanted(slug, wanted) {
    if wanted == () { return true; }
    if type_of(wanted) != "array" { return true; }
    if wanted.len() == 0 { return true; }
    for w in wanted {
        if w == slug { return true; }
    }
    false
}

fn conf_score(c) {
    if c == "high" { return 4; }
    if c == "medium_high" { return 3; }
    if c == "medium" { return 2; }
    if c == "low" { return 1; }
    0
}

fn report_score(report) {
    let score = 0;
    if report == () { return 0; }
    if report.sites == () { return 0; }
    for site in report.sites {
        if site.exclude == true { continue; }
        let c = if site.confidence != () { site.confidence } else { "" };
        score += conf_score(c);
    }
    score
}

fn method_block() {
    let p = "";
    p += "Repo: /Volumes/DATA/workspace/datacenter-probe (Datacenter Probe).\n";
    p += "Already surveyed — DO NOT add these: 贵安/guian 26.368N 106.490E; 乌兰察布/ulanqab 41.018N 113.116E; ";
    p += "阳泉/yangquan 37.860N 113.623E; 中卫/zhongwei 37.637N 105.347E; 克拉玛依/karamay 45.545N 84.870E.\n";
    p += "Method (same as notes/*/VERIFICATION_CATALOG.md):\n";
    p += "1. Pin a campus origin (not city hall). Search radius 50 km.\n";
    p += "2. Query Overpass (POST https://overpass-api.de/api/interpreter) for nwr telecom=data_center|data_centre ";
    p += "and name~数据中心|云计算|智算 around the origin. Save the JSON you used.\n";
    p += "3. Web-search 2024-2026 government/press reports for operators and park names. Reports are clues, not proof.\n";
    p += "4. Fetch Esri World Imagery. Prefer python3 scripts/fetch_esri_mosaic.py --lat --lon --z 16 --half 5 --out /tmp/<slug>.jpg ";
    p += "then read_file the JPEG. You MUST look at imagery before claiming halls exist.\n";
    p += "Count as a hall: huge courtyard-less rectangles, modular rows, rooftop CRAH/chillers, pads + cranes.\n";
    p += "Exclude: tanks/stacks (chem), greenhouses, ordinary factories, housing, PV fields themselves, unlabeled warehouses.\n";
    p += "Do not write an operator as fact without an OSM name, plaque, or planning map. Unlabeled halls stay 候选.\n";
    p += "Use tools. An empty sites list is valid ONLY after Overpass + at least one Esri mosaic around the likely park.\n";
    p
}

fn survey_prompt(c) {
    let p = method_block();
    p += "TASK: survey candidate hub " + c.city + " (slug=" + c.slug + ", region=" + c.region + ").\n";
    p += "Starting clue — NOT a finding, you must independently verify: " + c.hint + "\n";
    p += "Geocode the park first (Nominatim or news+OSM). Then Overpass around:50000. Then Esri z16/z17.\n";
    p += "worth_adding=true only if there is at least one satellite-visible or OSM-named datacenter campus ";
    p += "distinct from the five existing cities, with confidence high or medium_high.\n";
    p += "worth_adding=false if you only find plans/empty fields, or the park is the same corridor as 乌兰察布/贵安/中卫.\n";
    p += "origin_* must be the main campus, 6 decimal degrees or fewer. Site ids like ZB-ALI, HL-TENCENT.\n";
    p += "confidence one of: high, medium_high, medium, low. status e.g. operational, under_construction, mixed, excluded.\n";
    p += "Do not edit repo files in this phase. Report structured output only.\n";
    p
}

fn verify_prompt(item_json) {
    let p = method_block();
    p += "TASK: adversarially verify this survey report. Default real=false and worth_adding=false unless you independently ";
    p += "re-query Overpass AND look at Esri imagery yourself. Do not trust the report's coordinates or hall counts.\n";
    p += "Set real=true only with concrete evidence you inspected (OSM element id/name and/or hall morphology on a tile you fetched).\n";
    p += "Set worth_adding=true only if real=true AND the campus is not one of the five existing cities AND at least one ";
    p += "non-excluded site is confidence high or medium_high.\n";
    p += "If the origin is wrong, put corrected origin_lat/origin_lon/origin_name.\n";
    p += "Survey JSON follows:\n";
    p += item_json;
    p += "\n";
    p
}

fn add_prompt(picked_json, max_n) {
    let p = "";
    p += "You are adding verified datacenter hub cities to /Volumes/DATA/workspace/datacenter-probe.\n";
    p += "Work on the current git branch. Do NOT commit. Do NOT push.\n";
    p += "Add at most " + max_n + " cities from the confirmed list, in the given order. Skip a city if imagery fetch fails badly.\n";
    p += "Confirmed cities JSON:\n";
    p += picked_json;
    p += "\n";
    p += "For EACH added city, match existing style (贵安/阳泉/中卫/克拉玛依):\n";
    p += "A) notes/<slug>/findings.json — origin, search_radius_km=50, imagery Esri World Imagery 2026-08, sites array.\n";
    p += "B) notes/<slug>/osm_<slug>.json — raw Overpass dump you actually fetched.\n";
    p += "C) notes/<slug>/VERIFICATION_CATALOG.md — Chinese catalog like notes/zhongwei/VERIFICATION_CATALOG.md.\n";
    p += "D) Esri mosaics via python3 scripts/fetch_esri_mosaic.py (already in repo):\n";
    p += "   overview z15 or z16 half=6; campus z17 half=5. Write screenshots/<slug>/*.jpg. _tiles/ is gitignored.\n";
    p += "E) scripts/annotate_plates.py — add MOSAICS metadata (must match fetch lat/lon/z/half) and PLATESPEC boxes in WGS84.\n";
    p += "   Run python3 scripts/annotate_plates.py so docs/plates/<slug>/ exists.\n";
    p += "F) scripts/render_city_pages.py — append a PAGES dict in the same terse Chinese voice as the other four cities.\n";
    p += "   Update HEAD city-nav so every generated city page links the new slugs. Then run the renderer.\n";
    p += "G) docs/index.html — keep the original 五座城 grid. Add a second section 续卷 · 东数西算枢纽 with new city cards.\n";
    p += "   Do not pretend the new cities were in the 2022 智东西 article.\n";
    p += "H) README.md — add rows to the GitHub Pages table and 结论摘要. Say they are a continuation, not the original five.\n";
    p += "I) docs/ulanqab/index.html is hand-written; add a small city-nav to the other cities if missing, plus the new slugs.\n";
    p += "Prose: specific coordinates, OSM names, hall counts. No hype. Unnamed halls stay 候选. Exclusions listed.\n";
    p += "Leaflet PROBE JSON: origin, originName, radiusKm 50, sites with pos/color/note.\n";
    p += "Colors: #c23b22 construction/high, #2ec4b6 operational named, #c45c26 candidate, #7a7164 excluded.\n";
    p += "After writing, run the renderer and annotator. Return slugs added and key files written.\n";
    p
}

let max_cities = 3;
let wanted = ();
if args != () {
    if args.max_cities != () { max_cities = args.max_cities; }
    if args.candidates != () { wanted = args.candidates; }
}
if max_cities < 1 { max_cities = 1; }
if max_cities > 6 { max_cities = 6; }

let pool = [
    #{
        slug: "zhangbei",
        city: "张北",
        region: "Hebei",
        hint: "张家口张北县，京津冀算力枢纽。公开报道里的阿里巴巴张北数据中心、秦淮、腾讯等。不要和乌兰察布走廊搞混。",
    },
    #{
        slug: "huailai",
        city: "怀来",
        region: "Hebei",
        hint: "张家口怀来 / 官厅水库一带，京津冀枢纽。报道有腾讯怀来、秦淮数据、阿里。和张北是不同县城。",
    },
    #{
        slug: "horinger",
        city: "和林格尔",
        region: "Inner Mongolia",
        hint: "呼和浩特和林格尔新区 / 云谷，内蒙古枢纽另一翼。移动、联通、华为云报道。约 40.4N 111.8E，不是乌兰察布。",
    },
    #{
        slug: "qingyang",
        city: "庆阳",
        region: "Gansu",
        hint: "甘肃东数西算枢纽，庆阳西峰 / 数据中心集群。华为、电信等报道。戈壁/黄土沟壑上的新园。",
    },
    #{
        slug: "shaoguan",
        city: "韶关",
        region: "Guangdong",
        hint: "粤港澳大湾区枢纽韶关数据中心集群。粤北，不是广州市区。找集群主园区而不是市政府。",
    },
    #{
        slug: "wuhu",
        city: "芜湖",
        region: "Anhui",
        hint: "长三角枢纽芜湖集群。找数据中心园区/智算中心，不要把普通沿江工厂算进去。",
    },
];

let worklist = [];
for c in pool {
    if slug_wanted(c.slug, wanted) { worklist.push(c); }
}
if worklist.len() == 0 {
    pause("verification", "No candidates. Pass args.candidates as slugs (zhangbei, huailai, horinger, qingyang, shaoguan, wuhu).");
}

phase("Survey");
log("surveying " + worklist.len().to_string() + " hubs, will add up to " + max_cities.to_string());

let sjobs = [];
for c in worklist {
    sjobs.push(#{
        prompt: survey_prompt(c),
        label: "survey:" + c.slug,
        capability_mode: "all",
        output_schema: survey_schema,
    });
}
let sresults = parallel(sjobs);

let surveyed = [];
let si = 0;
for r in sresults {
    let c = worklist[si];
    if r != () && r.success && r.output != () {
        surveyed.push(#{ cand: c, report: r.output });
        let flag = "no";
        if r.output.worth_adding == true { flag = "yes"; }
        log(c.slug + " survey worth_adding=" + flag);
    } else {
        log(c.slug + " survey failed or empty");
    }
    si += 1;
}

let to_verify = [];
for item in surveyed {
    let report = item.report;
    let has_sites = report.sites != () && report.sites.len() > 0;
    if report.worth_adding == true || has_sites {
        to_verify.push(item);
    }
}
if to_verify.len() == 0 {
    complete(#{ summary: "No candidate hubs produced sites worth verifying.", added: [] });
}

phase("Verify");
let vjobs = [];
for item in to_verify {
    let payload = json_encode(item);
    vjobs.push(#{
        prompt: verify_prompt(payload),
        label: "verify:" + item.cand.slug,
        capability_mode: "all",
        output_schema: verdict_schema,
    });
}
let vresults = parallel(vjobs);

let confirmed = [];
let vi = 0;
for v in vresults {
    let item = to_verify[vi];
    let slug = item.cand.slug;
    if v != () && v.success && v.output != () && v.output.real == true && v.output.worth_adding == true {
        let ev = trimmed(v.output.evidence);
        if ev != "" {
            let report = item.report;
            if v.output.origin_lat != () { report.origin_lat = v.output.origin_lat; }
            if v.output.origin_lon != () { report.origin_lon = v.output.origin_lon; }
            if v.output.origin_name != () { report.origin_name = v.output.origin_name; }
            let sc = report_score(report);
            confirmed.push(#{
                slug: slug,
                city: item.cand.city,
                region: item.cand.region,
                score: sc,
                report: report,
                evidence: ev,
                reason: trimmed(v.output.reason),
            });
            log(slug + " confirmed score=" + sc.to_string());
        } else {
            log(slug + " rejected: real but empty evidence");
        }
    } else {
        log(slug + " rejected by verifier");
    }
    vi += 1;
}
if confirmed.len() == 0 {
    complete(#{ summary: "Verifiers rejected every hub. Nothing added.", added: [] });
}

let picked = [];
while picked.len() < max_cities {
    let best_i = -1;
    let best_score = -1;
    let ci = 0;
    for c in confirmed {
        let already = false;
        for p in picked {
            if p.slug == c.slug { already = true; }
        }
        if !already && c.score > best_score {
            best_score = c.score;
            best_i = ci;
        }
        ci += 1;
    }
    if best_i < 0 { break; }
    picked.push(confirmed[best_i]);
}
log("adding " + picked.len().to_string() + " cities");

phase("Add");
let nstr = picked.len().to_string();
let add_r = agent(add_prompt(json_encode(picked), nstr), #{
    label: "add-cities",
    capability_mode: "all",
    output_schema: add_schema,
});
if add_r == () || !add_r.success {
    pause("infra", "Add step failed. Resume after inspecting the workspace, or run the add phase manually.");
}

let added = [];
if add_r.output != () && add_r.output.added != () { added = add_r.output.added; }
let summary = "Added " + added.len().to_string() + " cities.";
if add_r.output != () && add_r.output.summary != () { summary = add_r.output.summary; }
complete(#{ summary: summary, added: added, picked: picked });
