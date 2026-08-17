#!/usr/bin/env python3
"""Build the World by Joe mosaic-globe marks.

The coastlines are stored as real latitude/longitude, then ORTHOGRAPHICALLY projected — the
view you get looking at a sphere from far away. That is what makes landmasses compress toward
the rim instead of sitting flat, which a plate-carree/Mercator layout can never do.

Each tile asks: inverse-project my centre back to lat/lon — am I on land? A graticule of
meridians and parallels is then drawn over the tiles like the leading in a stained-glass panel.
Resolution, view centre and graticule spacing are all single numbers below.
"""
from math import radians, degrees, sin, cos, asin, atan2, hypot, sqrt

CX = CY = 60.0
R   = 52.0            # disc radius in SVG units = the sphere's radius
LAT0, LON0 = 12.0, -84.0     # view centred on the Americas

INK        = "#2B2118"
LAND_COLS  = ["#C8992F","#D9B441","#C8992F","#B8862B","#D9B441","#C0522C","#C8992F","#D9B441"]
OCEAN_COLS = ["#4E9AA6","#46909B","#5AA3AE","#4E9AA6","#469BA6","#54A0AB"]

# Coarse coastlines in (lon, lat). Enough for a logo, nothing like an atlas.
NORTH_AND_CENTRAL = [
    (-166,65),(-156,71),(-135,70),(-115,69),(-100,68),(-85,70),(-73,68),(-65,62),
    (-57,54),(-53,47),(-65,44),(-70,41),(-75,36),(-79,33),(-81,30),(-80,25.5),
    (-84,29.5),(-89,29),(-94,29.5),(-97,26),(-97,21),(-92,18.5),(-87,21.5),(-87,18),
    (-83,15),(-83,11),(-78,9),(-83,8),(-88,13),(-95,16),(-101,17),(-106,21),
    (-110,24),(-114,28),(-117,32),(-122,37),(-124,42),(-124,48),(-131,54),(-140,59),
    (-150,59),(-158,56),
]
SOUTH = [
    (-78,9),(-72,11),(-62,10),(-52,5),(-45,-2),(-35,-6),(-38,-13),(-40,-22),
    (-48,-26),(-54,-34),(-58,-38),(-62,-41),(-66,-47),(-69,-52),(-72,-54),
    (-74,-48),(-73,-40),(-71,-30),(-70,-20),(-75,-14),(-79,-6),(-81,0),(-78,6),
]
CONTINENTS = [NORTH_AND_CENTRAL, SOUTH]

# Inland water, subtracted from the land above. Both are drawn LARGER than life: at this tile
# size a true-scale Hudson Bay or Gulf of Mexico is under one tile across and vanishes, and
# they are the two features that make the continent instantly legible.
HUDSON_BAY = [(-96,51),(-97,63),(-88,66),(-76,64),(-74,54),(-80,49),(-89,48)]
GULF_OF_MEXICO = [(-98,19),(-99,29),(-92,32),(-84,31),(-82,25),(-85,20),(-92,17.5)]
SEAS = [HUDSON_BAY, GULF_OF_MEXICO]

_la0, _lo0 = radians(LAT0), radians(LON0)

def project(lon, lat):
    """Forward orthographic. Returns (x, y, visible) with y measured UP."""
    la, lo = radians(lat), radians(lon)
    cosc = sin(_la0)*sin(la) + cos(_la0)*cos(la)*cos(lo-_lo0)
    x = R * cos(la) * sin(lo-_lo0)
    y = R * (cos(_la0)*sin(la) - sin(_la0)*cos(la)*cos(lo-_lo0))
    return x, y, cosc >= 0

def unproject(x, y):
    """Inverse orthographic: a point on the disc back to (lon, lat), or None past the rim."""
    rho = hypot(x, y)
    if rho > R:
        return None
    if rho < 1e-9:
        return LON0, LAT0
    c = asin(min(1.0, rho/R))
    lat = asin(cos(c)*sin(_la0) + (y/rho)*sin(c)*cos(_la0))
    lon = _lo0 + atan2(x*sin(c), rho*cos(c)*cos(_la0) - y*sin(c)*sin(_la0))
    return degrees(lon), degrees(lat)

def in_poly(poly, lon, lat):
    hit = False
    n = len(poly)
    for i in range(n):
        ax, ay = poly[i]
        bx, by = poly[(i+1) % n]
        if (ay > lat) != (by > lat) and lon < ax + (lat-ay)/(by-ay)*(bx-ax):
            hit = not hit
    return hit

def is_land(lon, lat):
    if any(in_poly(s, lon, lat) for s in SEAS):
        return False
    return any(in_poly(p, lon, lat) for p in CONTINENTS)

def stable(a, b):
    """Deterministic colour pick, so rebuilding never reshuffles the tiles."""
    return (a*73856093 ^ b*19349663 ^ 0x9E37) & 0xFFFF

def graticule(step=30, samples=180, width=1.35, opacity=0.85):
    """Meridians and parallels as they actually curve in this projection."""
    out = []
    def path(pts):
        if len(pts) < 2:
            return
        d = "M%.2f %.2f" % pts[0] + "".join("L%.2f %.2f" % p for p in pts[1:])
        out.append('    <path d="%s"/>' % d)
    def walk(coords):
        run = []
        for lon, lat in coords:
            x, y, vis = project(lon, lat)
            if vis:
                run.append((CX + x, CY - y))      # flip to SVG's y-down
            else:
                path(run); run = []
        path(run)
    for lat in range(-90+step, 90, step):                    # parallels
        walk([(-180 + 360*i/samples, lat) for i in range(samples+1)])
    lon = LON0 - 180
    while lon < LON0 + 180:                                  # meridians
        walk([(lon, -90 + 180*i/samples) for i in range(samples+1)])
        lon += step
    return ('  <g fill="none" stroke="%s" stroke-width="%.2f" stroke-opacity="%.2f"\n'
            '     stroke-linecap="round">\n%s\n  </g>\n'
            % (INK, width, opacity, "\n".join(out))) if out else ""

def rules(n, cols, rows, width=2.0, opacity=1.0):
    """A few straight rules instead of a line at every tile edge. Positions are given as tile
    indices so they land exactly on tile boundaries — deliberate composition, not a mesh."""
    if not cols and not rows:
        return ""
    cell = (2*R)/n
    x0 = y0 = CX - R
    seg = []
    for c in cols:
        x = x0 + c*cell
        seg.append('    <line x1="%.2f" y1="0" x2="%.2f" y2="120"/>' % (x, x))
    for r in rows:
        y = y0 + r*cell
        seg.append('    <line x1="0" y1="%.2f" x2="120" y2="%.2f"/>' % (y, y))
    return ('  <g stroke="%s" stroke-width="%.2f" stroke-opacity="%.2f" stroke-linecap="butt">\n'
            '%s\n  </g>\n' % (INK, width, opacity, "\n".join(seg)))


def _vnoise(x, y, s):
    """Smooth value noise on a lattice — the same idea the mosaic generator uses."""
    from math import floor
    ix, iy = int(floor(x)), int(floor(y))
    fx, fy = x - ix, y - iy
    def h(a, b):
        v = (a*73856093 ^ b*19349663 ^ s*83492791) & 0x7FFFFFFF
        v = (v ^ (v >> 13)) * 1274126177 & 0x7FFFFFFF
        return ((v ^ (v >> 16)) & 0xFFFF) / 65535.0
    ux, uy = fx*fx*(3-2*fx), fy*fy*(3-2*fy)
    a, b = h(ix, iy), h(ix+1, iy)
    c, d = h(ix, iy+1), h(ix+1, iy+1)
    return a + (b-a)*ux + (c-a)*uy + (a-b-c+d)*ux*uy

def subdivision(n, seed, depth=9, width=1.05, opacity=1.0, minspan=1,
                patch=2.2, big=0.85, small=0.11):
    """Seams from the mosaic generator's own rule. A smooth detail map decides the block size
    each ZONE wants: where it reads low, a panel stops early and stays large; where it reads
    high, the block keeps splitting into small ones. That contrast — not uniform random
    cutting — is what gives the artwork its range of tile sizes, so the seams inherit it too.
    Cuts favour halves and thirds, as they do in the artwork, so seams line up."""
    cell = (2*R)/n
    x0 = y0 = CX - R
    rng = seed | 1
    def nxt():
        nonlocal rng
        rng = (rng*1103515245 + 12345) & 0x7FFFFFFF
        return rng / 0x7FFFFFFF
    maxb, minb = n*big, max(1.2, n*small)
    seg = []
    def split(c0, r0, c1, r1, d):
        w, h = c1-c0, r1-r0
        longest = max(w, h)
        mx, my = (c0+c1)/2.0/n, (r0+r1)/2.0/n
        f = _vnoise(mx*patch, my*patch, seed)
        f = min(1.0, max(0.0, 0.5 + (f-0.5)*1.9))          # sharpen the zones
        target = maxb * (minb/maxb) ** f                    # what this zone wants
        if d == 0 or longest <= target or longest < 2*minspan:
            return
        vert = w >= h
        span = w if vert else h
        lo, hi = minspan, span - minspan
        if hi <= lo:
            return
        r = nxt()
        frac = 0.5 if r < 0.42 else (1/3.0 if r < 0.62 else (2/3.0 if r < 0.82 else nxt()))
        k = int(round(span*frac))
        k = max(lo, min(hi, k))
        if vert:
            x = x0 + (c0+k)*cell
            seg.append('    <line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f"/>'
                       % (x, y0+r0*cell, x, y0+r1*cell))
            split(c0, r0, c0+k, r1, d-1); split(c0+k, r0, c1, r1, d-1)
        else:
            y = y0 + (r0+k)*cell
            seg.append('    <line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f"/>'
                       % (x0+c0*cell, y, x0+c1*cell, y))
            split(c0, r0, c1, r0+k, d-1); split(c0, r0+k, c1, r1, d-1)
    split(0, 0, n, n, depth)
    return ('  <g stroke="%s" stroke-width="%.2f" stroke-opacity="%.2f" stroke-linecap="butt">\n'
            '%s\n  </g>\n' % (INK, width, opacity, "\n".join(seg))) if seg else ""

def build(path, n=14, grout=0.85, stroke=5, uid="wbj", grat=30, grat_w=1.35, grat_op=0.85,
          rule_cols=(), rule_rows=(), rule_w=2.0, rule_op=1.0,
          subdiv=0, subdiv_seed=7, subdiv_w=1.05, subdiv_min=3):
    cell = (2*R)/n
    x0 = y0 = CX - R
    rects = []
    for r in range(n):
        for c in range(n):
            x = x0 + c*cell
            y = y0 + r*cell
            mx, my = x + cell/2, y + cell/2
            if (mx-CX)**2 + (my-CY)**2 > (R + cell*0.6)**2:
                continue
            ll = unproject(mx-CX, CY-my)
            land = bool(ll) and is_land(*ll)
            pal = LAND_COLS if land else OCEAN_COLS
            rects.append('    <rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s"/>'
                         % (x+grout/2, y+grout/2, cell-grout, cell-grout,
                            pal[stable(r+1, c+1) % len(pal)]))
    g = graticule(grat, width=grat_w, opacity=grat_op) if grat else ""
    g += rules(n, rule_cols, rule_rows, rule_w, rule_op)
    if subdiv:
        g += subdivision(n, subdiv_seed, subdiv, subdiv_w, minspan=subdiv_min)
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="120" height="120"\n'
           '     role="img" aria-label="World by Joe">\n'
           '  <title>World by Joe</title>\n'
           '  <defs><clipPath id="%s"><circle cx="60" cy="60" r="52"/></clipPath></defs>\n'
           '  <circle cx="60" cy="60" r="52" fill="%s"/>\n'
           '  <g clip-path="url(#%s)">\n'
           '   <g shape-rendering="crispEdges">\n%s\n   </g>\n%s  </g>\n'
           '  <circle cx="60" cy="60" r="52" fill="none" stroke="%s" stroke-width="%d"/>\n'
           '</svg>\n') % (uid, INK, uid, "\n".join(rects), g, INK, stroke)
    open(path, "w").write(svg)
    return len(rects)

if __name__ == "__main__":
    # The chosen mark: 16 tiles across, seams from detail-map subdivision on seed 61.
    N, SEED = 16, 61
    build("worldbyjoe-mark.svg", n=N, grout=0, grat=0, uid="wbj",
          subdiv=9, subdiv_seed=SEED, subdiv_w=1.0, subdiv_min=1)
    # favicon: coarser tiles and only a few seams, so it survives 16-32 px
    build("worldbyjoe-favicon.svg", n=8, grout=0, grat=0, stroke=6, uid="wbjs",
          subdiv=3, subdiv_seed=SEED, subdiv_w=1.6, subdiv_min=2)

    mark = open("worldbyjoe-mark.svg").read()
    inner = mark[mark.index("<defs>"):mark.rindex("</svg>")]
    FONT = ("Futura,'Futura PT','Century Gothic','Avenir Next',Questrial,"
            "'Trebuchet MS',sans-serif")

    def lockup(fname, w, h, body):
        open(fname, "w").write(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d"\n'
            '     role="img" aria-label="World by Joe">\n  <title>World by Joe</title>\n%s\n</svg>\n'
            % (w, h, w, h, body))

    lockup("worldbyjoe-lockup.svg", 430, 120,
           '  <g>%s</g>\n'
           '  <text x="150" y="56" font-family="%s" font-size="38" font-weight="600"\n'
           '        letter-spacing="6.2" fill="#2B2118">WORLD</text>\n'
           '  <text x="150" y="90" font-family="%s" font-size="21" font-weight="400"\n'
           '        letter-spacing="4.6" fill="#8A7F6D">BY '
           '<tspan font-weight="600" fill="#2B2118">JOE</tspan></text>' % (inner, FONT, FONT))

    lockup("worldbyjoe-lockup-inline.svg", 560, 120,
           '  <g>%s</g>\n'
           '  <text x="150" y="74" font-family="%s" font-size="34" font-weight="600"\n'
           '        letter-spacing="5.4" fill="#2B2118">WORLD '
           '<tspan font-weight="400" fill="#8A7F6D">BY</tspan> JOE</text>' % (inner, FONT))
    print("built the World by Joe logo set")
