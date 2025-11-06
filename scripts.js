  const byId = id => document.getElementById(id);
  const el = (tag, cls) => { const e=document.createElement(tag); if(cls) e.className=cls; return e; }

  const STATE = { raw:[], filtered:[], page:1, pageSize:12, sort:'date_desc', source:'', search:'', line:'' };

  const LOGO_BASE = "https://raw.githubusercontent.com/passakornDextra/competitorWatch/main/logos/";
  const LOGO_DEFAULT = LOGO_BASE + "0 Logo Dextra RGB Web Colors.png";

  const LINE_LOGOS = {
    "crp": LOGO_BASE + "CRP_16x9_white.png",
    "bars": LOGO_BASE + "Bars_16x9_white.png",
    "geotec": LOGO_BASE + "Geo_16x9_white.png"
  };

  const normalize = s => (s || "")
    .toLowerCase()
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .replace(/[\u2018\u2019]/g, "'")
    .replace(/[\u2013\u2014]/g, "-")
    .replace(/[^a-z0-9]+/g, " ")
    .replace(/\s+/g, " ").trim();

  /* --- Canonical logos (fixed spelling: firep minova) --- */
  const LOGO_MAP = {
    "dywidag": "DYWIDAG_16x9.png",
    "anker schroeder": "Anker_Schroeder_16x9.png",
    "ancon": "Leviat_Ancon_16x9.png",
    "stahlwerk annahutte": "SAH_Stahlwerk_Annahutte_16x9.png",
    "sah": "SAH_Stahlwerk_Annahutte_16x9.png",
    "nvent lenton": "nVent_Lenton_16x9.png",
    "lenton": "nVent_Lenton_16x9.png",
    "macalloy": "Macalloy_16x9.png",
    "moment": "Leviat_Moment_16x9.png",
    "firep minova": "FiReP_16x9.png",
    "williams form": "Williams_Form_16x9.png",
    "nmb splice sleeve": "NMB_Splice_Sleeve_16x9.png",
    "boowon bms": "Boowon_BMS_16x9.png",
    "mateenbar": "Mateenbar_16x9.png",
    "mst bar": "MST_Bar_16x9.png",
    "linxion": "linxion_16x9.png",
    "peikko": "PeikkoGroup_16x9.png"
  };

  /* --- Aliases coming from CSV (normalize to canonical) --- */
  const LOGO_ALIASES = {
    "williams": "williams form",
    "williams form engineering": "williams form",
    "williams form engineering corp": "williams form",
    "william form": "williams form",
    "moment (leviat)": "moment",
    "leviat moment": "moment",
    "moment-leviat": "moment",
    "moment leviat": "moment",
    "ancon (leviat)": "ancon",
    "minova apac": "firep minova",
    "firep": "firep minova",
    "fi rep": "firep minova",
    "fi rep minova": "firep minova",
    "mstbar": "mst bar",
    "mst-bar": "mst bar",
    "sah annahutte": "stahlwerk annahutte",
    "stahlwerk annahuette": "stahlwerk annahutte",

  };

  /* --- Product lines per canonical source --- */
  const LINE_MAP = {
    "moment": ["CRP"],
    "ancon": ["CRP"],
    "nvent lenton": ["CRP"],
    "nmb splice sleeve": ["CRP"],
    "boowon bms": ["CRP"],
    "dywidag": ["Bars", "Geotec"],
    "anker schroeder": ["Bars"],
    "macalloy": ["Bars"],
    "williams form": ["Bars"],
    "stahlwerk annahutte": ["Bars", "Geotec"],
    "sah": ["Bars", "Geotec"],
    "mateenbar": ["Geotec"],
    "mst bar": ["Geotec"],
    "firep minova": ["Geotec"],
    "peikko": ["CRP"],
    "linxion": ["CRP"],
  };

  /* --- Display name mapping (what the user sees) --- */
  const DISPLAY_NAME = {
    "moment": "Moment (Leviat)",
    "ancon": "Ancon (Leviat)",
    "nvent lenton": "nVent LENTON",
    "firep minova": "FiReP Minova",
    "dywidag": "DYWIDAG",
    "anker schroeder": "Anker Schroeder",
    "stahlwerk annahutte": "Stahlwerk Annahütte",
    "sah": "Stahlwerk Annahütte",
    "macalloy": "Macalloy",
    "williams form": "Williams Form",
    "nmb splice sleeve": "NMB Splice Sleeve",
    "mateenbar": "Mateenbar",
    "mst bar": "MST Bar",
    "boowon bms": "Boowon BMS",
    "peikko": "Peikko",
    "linxion": "Linxion",
    "nmb splice sleeve": "NMB Splice Sleeve"
  };

  function displayFor(canon) {
    if (!canon) return '';
    if (DISPLAY_NAME[canon]) return DISPLAY_NAME[canon];
    return canon.replace(/\b\w/g, c => c.toUpperCase());
  }

  function logoFileFor(canonical) {
    if (LOGO_MAP[canonical]) return LOGO_MAP[canonical];
    let bestKey = null;
    for (const k in LOGO_MAP) {
      if (canonical.includes(k)) { if (!bestKey || k.length > bestKey.length) bestKey = k; }
    }
    return bestKey ? LOGO_MAP[bestKey] : null;
  }

  function canonicalFor(name) {
    const key = normalize(name);
    return LOGO_ALIASES[key] || key;
  }

  function logoSrcFor(nameOrCanon) {
    const canonical = canonicalFor(nameOrCanon);
    const file = logoFileFor(canonical);
    return file ? (LOGO_BASE + file) : null;
  }

  function linesFor(name) {
    const canonical = canonicalFor(name);
    return LINE_MAP[canonical] || [];
  }

  function setHeaderLogo() {
    const img = byId("brandImg");
    const companyLogo = STATE.source && logoSrcFor(STATE.source); // STATE.source is canonical
    const lineKey = (STATE.line || '').toLowerCase();
    const lineSrc = LINE_LOGOS[lineKey];
    const src = companyLogo || lineSrc || LOGO_DEFAULT;

    img.hidden = false;
    img.alt = companyLogo ? displayFor(STATE.source) : (STATE.line || 'Dextra');
    img.src = src;
    img.onerror = () => { img.onerror = null; img.src = LOGO_DEFAULT; };
  }

  function parseDate(v) {
    if (!v) return null;
    const d = new Date(v);
    if (!isNaN(d)) return d;
    const m = String(v).match(/(\d{1,2})[\/.\-](\d{1,2})[\/.\-](\d{2,4})/);
    if (m) {
      const [_, d1, m1, y1] = m;
      const yr = y1.length === 2 ? (Number(y1) + 2000) : Number(y1);
      return new Date(yr, Number(m1) - 1, Number(d1));
    }
    return null;
  }

  function loadCSV() {
    Papa.parse('export_combined.csv', {
      download: true, header: true, skipEmptyLines: true,
      complete: (res) => {
        const rows = res.data.map(r => {
          const srcRaw   = r.Source?.trim() || '';
          const srcCanon = canonicalFor(srcRaw);

          // Normalize ISO date (prefer CSV DateISO; fallback to parsed Date/DateText)
          const isoCSV = (r.DateISO || '').trim().slice(0, 10); // YYYY-MM-DD
          const fallbackObj = parseDate(r.Date || r.DateText);
          const isoFallback = fallbackObj ? fallbackObj.toISOString().slice(0,10) : '';
          const dateISO = isoCSV || isoFallback;

          // Robust numeric sort key; blank → 0 (goes to bottom on DESC)
          const dateKeyNum = dateISO ? Number(dateISO.replace(/-/g, '')) : 0;

          return {
            Title: r.Title?.trim() || '',
            DateText: r.DateText?.trim() || '',
            DateISO: dateISO,
            DateObj: fallbackObj || null,
            DateKeyNum: dateKeyNum,
            Link: r.Link?.trim() || '',
            Image: r.Image?.trim() || '',
            Summary: r.Summary?.trim() || '',
            Source: srcRaw,                      // original
            SourceCanon: srcCanon,               // normalized key
            SourceDisplay: displayFor(srcCanon), // pretty label
            Lines: linesFor(srcRaw)
          };
        });

        STATE.raw = rows;
        hydrateSources(rows);

        const params = new URLSearchParams(location.search);
        const preCompany = params.get('company');
        const preLine = params.get('line');
        const preSearch = params.get('search');
        const preSort = params.get('sort');
        
        if (preCompany) {
          const cand = canonicalFor(preCompany);
          if ([...byId('source').options].some(o => o.value === cand)) {
            byId('source').value = cand;
            STATE.source = cand;
          }
        }
        if (preLine && ["CRP","Bars","Geotec"].includes(preLine)) {
          byId('line').value = preLine;
          STATE.line = preLine;
        }
        if (preSearch) {
          byId('search').value = preSearch;
          STATE.search = preSearch;
        }
        if (preSort && ['date_desc', 'date_asc', 'title_asc', 'title_desc'].includes(preSort)) {
          byId('sort').value = preSort;
          STATE.sort = preSort;
        }

        setHeaderLogo();
        applyFilters();
      },
      error: () => { byId('status').textContent = 'Could not load export_combined.csv.'; }
    });
  }

  /* Populate dropdown using canonical values but display nice names */
  function hydrateSources(rows) {
    const sel = byId('source');
    const uniqCanon = [...new Set(rows.map(r => r.SourceCanon).filter(Boolean))]
      .sort((a,b) => displayFor(a).localeCompare(displayFor(b)));
    uniqCanon.forEach(canon => {
      const o = el('option');
      o.value = canon;                   // filter by canonical
      o.textContent = displayFor(canon); // label users see
      sel.appendChild(o);
    });
  }

  function applyFilters() {
    const { source, sort, search, line } = STATE;
    let rows = STATE.raw.filter(r =>
      (!source || r.SourceCanon === source) &&
      (!line || (r.Lines && r.Lines.includes(line))) &&
      (!search || r.Title.toLowerCase().includes(search.toLowerCase()) || r.Summary.toLowerCase().includes(search.toLowerCase()))
    );

    rows.sort((a, b) => {
      switch (sort) {
        case 'title_asc':  return a.Title.localeCompare(b.Title);
        case 'title_desc': return b.Title.localeCompare(a.Title);
        case 'date_asc':
          return (a.DateKeyNum - b.DateKeyNum) ||
                 a.Title.localeCompare(b.Title);
        default: // date_desc
          return (b.DateKeyNum - a.DateKeyNum) ||
                 a.Title.localeCompare(b.Title);
      }
    });

    STATE.filtered = rows;
    STATE.page = 1;
    render();
  }

 

function render() {
  const grid = byId('grid');
  const rail = byId('rail');
  const status = byId('status');
  const pager = byId('pager');
  const count = byId('articleCount');

  const rows = STATE.filtered || [];
  const total = rows.length;

  // No results
  if (!total) {
    rail.hidden = true;
    grid.hidden = true;
    pager.hidden = true;
    count.hidden = true;
    status.hidden = false;
    status.textContent = 'No articles found.';
    return;
  }

  status.hidden = true;
  count.hidden = false;

  // Prepare top 5: center (1), left (2), right (2)
  const center = rows[0] || null;
  const leftStories  = rows.slice(1, 3);
  const rightStories = rows.slice(3, 5);

  // Render rail
  rail.hidden = false;
  const railLeft   = rail.querySelector('.rail-left');
  const railCenter = rail.querySelector('.rail-center');
  const railRight  = rail.querySelector('.rail-right');

  railLeft.innerHTML = '';
  railCenter.innerHTML = '';
  railRight.innerHTML = '';

  if (center)    railCenter.appendChild(card(center, 'lead'));
  leftStories.forEach(s  => railLeft.appendChild(card(s, 'side')));
  rightStories.forEach(s => railRight.appendChild(card(s, 'side')));

  // Render rest in grid with pagination
  const rest = rows.slice(5);
  grid.innerHTML = '';

  if (rest.length === 0) {
    grid.hidden = true;
    pager.hidden = true;
    count.textContent = `Showing ${Math.min(5, total)} of ${total} articles`;
    return;
  }

  grid.hidden = false;
  pager.hidden = false;

  const totalPages = Math.max(1, Math.ceil(rest.length / STATE.pageSize));
  if (STATE.page > totalPages) STATE.page = totalPages;

  const start = (STATE.page - 1) * STATE.pageSize;
  const end = start + STATE.pageSize;
  const pageRows = rest.slice(start, end);

  pageRows.forEach(r => grid.appendChild(card(r)));

  byId('pageInfo').textContent = `Page ${STATE.page} / ${totalPages}`;
  byId('prev').disabled = STATE.page <= 1;
  byId('next').disabled = STATE.page >= totalPages;

  const shownFrom = 5 + start + 1;
  const shownTo   = 5 + start + pageRows.length;
  count.textContent = `Welcome to Competitor News, now we scrape ${total} articles`;
}


  // Keep your existing prev/next listeners; they already call render().


  
function card(row, variant) {
  const c = el('article', 'card' + (variant ? ` card--${variant}` : ''));
  const img = el('img', 'thumb');
  img.loading = 'lazy';
  img.alt = row.Title || 'thumbnail';
  img.src = row.Image || 'data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22400%22 height=%22225%22><rect width=%22400%22 height=%22225%22 fill=%22%23f1f5f9%22/><text x=%2250%25%22 y=%2250%25%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 fill=%2394a3b8%22 font-size=%2218%22 font-family=%22system-ui%22 font-weight=%22600%22>No image available</text></svg>';
  img.onerror = () => {
    img.onerror = null;
    img.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="225"><rect width="400" height="225" fill="%23f1f5f9"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%2394a3b8" font-size="18" font-family="system-ui" font-weight="600">No image available</text></svg>';
  };
  c.appendChild(img);

  const p = el('div', 'pad');
  const h = el('h2', 'title'); h.textContent = row.Title || '(Untitled)';
  const meta = el('div', 'meta');

  const chip = el('span', 'chip');
  chip.textContent = row.SourceDisplay || 'Unknown';
  meta.append(chip);

  if (row.Lines && row.Lines.length) {
    row.Lines.forEach(L => {
      const ch = el('span', 'chip line'); ch.textContent = L; meta.append('•', ch);
    });
  }

  const date = el('span');
  date.textContent = row.DateISO || '';
  meta.append('•', date);

  const sum = el('p', 'summary'); sum.textContent = row.Summary || '';
  p.append(h, meta, sum);
  c.appendChild(p);

  const actions = el('div', 'actions');
  const a1 = el('a', 'link primary'); a1.href = row.Link || '#'; a1.target = '_blank'; a1.rel = 'noopener'; a1.textContent = 'Read Article';
  const a2 = el('a', 'link'); a2.href = `https://www.google.com/search?q=${encodeURIComponent((row.Title || '') + ' ' + (row.SourceDisplay || ''))}`; a2.target = '_blank'; a2.rel = 'noopener'; a2.textContent = 'Search More';
  actions.append(a1, a2);
  c.appendChild(actions);

  return c;
}

function filterCompaniesByLine(selectedLine) {
  const sel = byId('source');
  sel.innerHTML = ''; // Clear existing options

  // Always include "All Companies"
  const defaultOpt = el('option');
  defaultOpt.value = '';
  defaultOpt.textContent = 'All Companies';
  sel.appendChild(defaultOpt);

  // If no line selected, show all companies
  if (!selectedLine) {
    const uniqCanon = [...new Set(STATE.raw.map(r => r.SourceCanon).filter(Boolean))]
      .sort((a,b) => displayFor(a).localeCompare(displayFor(b)));
    uniqCanon.forEach(canon => {
      const o = el('option');
      o.value = canon;
      o.textContent = displayFor(canon);
      sel.appendChild(o);
    });
    return;
  }

  // Filter companies that have this line in LINE_MAP
  const uniqCanon = [...new Set(STATE.raw.map(r => r.SourceCanon).filter(Boolean))]
    .filter(canon => (LINE_MAP[canon] || []).includes(selectedLine))
    .sort((a,b) => displayFor(a).localeCompare(displayFor(b)));

  uniqCanon.forEach(canon => {
    const o = el('option');
    o.value = canon;
    o.textContent = displayFor(canon);
    sel.appendChild(o);
  });
}



const allowedLines = ["CRP", "Bars", "Geotec"];

byId('source').addEventListener('change', e => {
  STATE.source = e.target.value;
  setHeaderLogo();
  applyFilters();
});


byId('line').addEventListener('change', e => {
  STATE.line = e.target.value;
  filterCompaniesByLine(STATE.line); // Rebuild company dropdown
  setHeaderLogo();
  applyFilters();
});


byId('sort').addEventListener('change', e => {
  STATE.sort = e.target.value;
  applyFilters();
});

byId('search').addEventListener('input', e => {
  STATE.search = e.target.value;
  applyFilters();
});

byId('prev').addEventListener('click', () => {
  STATE.page = Math.max(1, STATE.page - 1);
  render();
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

byId('next').addEventListener('click', () => {
  const totalPages = Math.max(1, Math.ceil(STATE.filtered.length / STATE.pageSize));
  STATE.page = Math.min(totalPages, STATE.page + 1);
  render();
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

window.addEventListener('scroll', () => {
  const btn = byId('backToTop');
  btn.style.display = window.scrollY > 300 ? 'block' : 'none';
});


  setHeaderLogo();
  loadCSV();


  
