# Mosaic Tile Generator

A browser-based generator for algorithmic mosaic art. It is a single self-contained HTML file —
no install, no build step, no internet connection required once loaded. Open it and it runs.

## Try it

**[Mosaic Maker](https://worldbyjoe.github.io/MosaicTileGenerator/)**

You can also download `index.html` and double-click it — it runs offline.

## How it works

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

## Hexagonal tiling

Switching on **Hexagonal tiling** lays a uniform hex grid over the same design. Each hexagon
takes the colour of whichever rectangle sits under its centre, so a large calm rectangle
becomes a solid patch of hexagons while fine speckle varies hex by hex. The grid is a
resampling filter over the composition, not a separate generator, so the palette, colour runs,
patchiness and panel structure all carry through unchanged.

## Reproducing a piece

Every artwork is generated from a seed, so the same settings always produce the same image.
Exported PNGs carry their full settings inside the file as PNG metadata — use **Load settings**
and pick any PNG the page exported to restore that exact artwork, sliders and all.

## Printing

The export menu offers sizes up to 12000 px, which is 40 inches at 300 dpi. Canvas shapes are
labelled with the print sizes they fit, in either landscape or portrait. **Split into panels**
divides the piece into however many equal vertical panels the slider specifies and saves each
one as its own file, ready to print as a matched set of canvases.
