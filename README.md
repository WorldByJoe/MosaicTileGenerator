# Mosaic Tile Generator

Two browser-based generators for algorithmic mosaic art. Each is a single self-contained
HTML file — no install, no build step, no internet connection required once loaded. Open the
file (or the link below) and it runs.

## Try them

- **[Mosaic Maker](https://worldbyjoe.github.io/MosaicTileGenerator/)** — rectangular tile
  mosaics with a simulated oil-paint surface.
- **[Hex Mosaic Maker](https://worldbyjoe.github.io/MosaicTileGenerator/hex-mosaic-maker.html)** —
  hexagonal tilings with three pattern engines and a glazed-ceramic finish.

You can also just download either `.html` file and double-click it — they run offline.

## Mosaic Maker

A recursive-subdivision tile painting generator. A smooth noise "detail map" decides where
tiles should be large and where they break into fine speckle; the canvas is then cut
recursively, with cuts favouring exact halves and thirds so seams line up like real tilework.
Colours come from a weighted warm palette whose odds drift slowly across the panel, so hues
pool into neighbourhoods rather than scattering.

The surface is a mechanical paint simulation rather than a texture filter: each tile is
underpainted, then colour is applied by stamping bristle footprints along stroke paths. The
brush carries a paint load that depletes as it travels, so strokes break into dry-brush
fragments, and every stamp deposits into a height field that is lit once, globally, from the
upper left.

Controls cover composition, tile size distribution, palette weighting and finish. Notable
options: golden-ratio tiles, triptych mode (exports three separate print files), six stroke
styles, and print export up to 12000 px.

## Hex Mosaic Maker

Every hexagon is the same size — the interest lives in the pattern layer instead, which is how
hexagonal tile design actually works. Three engines:

- **Colour fields** — whole-hex colours drawn from the same palette machinery.
- **Pinwheel triangles** — each hexagon split into six triangles under a symmetry rule.
  Triangles from neighbouring hexes fuse across the seams into larger rhombi and stars.
- **Truchet ribbons** — arcs joining edge midpoints, randomly rotated. Because the ends land
  on the seam midpoints, neighbours continue each other's lines and ribbons cross the panel
  from a purely local rule.

## Reproducing a piece

Every artwork is generated from a seed, so the same settings always produce the same image.
Exported PNGs carry their full settings inside the file as PNG metadata — use **Load settings**
and pick any PNG the page exported to restore that exact artwork, sliders and all.

## Printing

The export menu offers sizes up to 12000 px, which is 40 inches at 300 dpi. Canvas shapes are
labelled with the print sizes they fit. Triptych mode saves three separate files, one per panel.
