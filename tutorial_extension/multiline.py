import bokeh.models
import pyopenms as oms

import rdkit.Chem
from bokeh.embed import file_html
from bokeh.io import save
from bokeh.models import HoverTool, ColumnDataSource, BoxZoomTool, Row, CustomJS, CustomJSHover
from bokeh.resources import CDN
from bokeh.util.browser import view
from rdkit.Chem.Draw import rdMolDraw2D
from bokeh.plotting import figure, show
from bokeh.layouts import row
import pandas as pd


def mol2svg(smiles):
    if smiles == "":
        return ""
    mol = rdkit.Chem.MolFromSmiles(smiles)
    d2d = rdMolDraw2D.MolDraw2DSVG(200, 100)
    d2d.DrawMolecule(mol)
    d2d.FinishDrawing()
    return d2d.GetDrawingText()


def main():
    molsmiles = "CC(=O)Oc1ccccc1C(=O)O"

    template = """
    {% block postamble %}
        <script src="https://code.jquery.com/jquery-3.4.1.min.js"></script>
        <script src="https://unpkg.com/@rdkit/rdkit/dist/RDKit_minimal.js"></script>
        <script>
            window
              .initRDKitModule()
              .then(function (RDKit) {
                console.log("RDKit version: " + RDKit.version());
                RDKitModule = RDKit;
                /**
                 * The RDKit module is now loaded.
                 * You can use it anywhere.
                 */
              })
              .then(initMol)
              .catch(() => {
                // handle loading errors here...
              });
            function initMol(){
                        var moldiv = Bokeh.documents[0].get_model_by_name('moldiv')
                        var smiles = "CC(=O)Oc1ccccc1C(=O)O";
                        var mol = RDKitModule.get_mol(smiles);
                        var svg = mol.get_svg();
                        moldiv.text = svg;
            }
            setTimeout(initMol, 500);
        </script>
    {% endblock %}
    """

    # prepare some data
    mzs = [1., 2., 3.5, 4., 5.]
    x = [[m, m] for m in mzs]
    itys = [6., 7., 2., 4., 5.]
    y = [[0, i] for i in itys]

    annotList = ["", "Oc1[c,n]cccc1", "", "c1[c,n]cccc1", ""]
    color = ["black" if annot == "" else "red" for annot in annotList]

    # create a new plot with a title and axis labels
    p = figure(title="Simple line example", x_axis_label='m/z', y_axis_label='Intensity',
               tools=['xwheel_zoom', 'xpan'], active_scroll='xwheel_zoom')

    source = ColumnDataSource({'mz': x, 'ity': y, 'annot': annotList, 'color': color})
    # add a line renderer with legend and line thickness to the plot
    p.multi_line(name="peaks", xs="mz", ys="ity", source=source, line_width=2, hover_line_width=3,
                 color="color")

    js_code = """
    var annot = cb_data.renderer.data_source.data.annot
    var moldiv = Bokeh.documents[0].get_model_by_name('moldiv');
    var smiles = "CC(=O)Oc1ccccc1C(=O)O";
    var mol = RDKitModule.get_mol(smiles);
    if (cb_data.index.indices.length >= 1 && annot[cb_data.index.indices[0]] != "")
    {
        var qmol = RDKitModule.get_qmol(annot[cb_data.index.indices[0]]);
        var mdetails = mol.get_substruct_match(qmol);
        moldiv.text = mol.get_svg_with_highlights(mdetails);
    } else {
        moldiv.text = mol.get_svg();
    }
    """ % annotList

    # args={'smiles': cr.data_source, 'segment': sr.data_source}
    cb = CustomJS(code=js_code)

    format_code = f"return value[1]"
    formatter = CustomJSHover(code=format_code)

    hover = HoverTool(
        tooltips="""
                    <div>
                    <div>
                        @annot
                    <div>
                        <b>m/z:</b> <span style="font-size: 12px; color: #696;">@mz{custom}</span><br>
                        <b>Intensity:</b> <span style="font-size: 12px; color: #796;">@ity{custom}</span>
                    </div>
                </div>
                """,
        callback=cb,
        formatters=
        {
            '@ity': formatter,
            '@mz': formatter,
        }
    )

    hover.line_policy = 'next'
    boxzoom = BoxZoomTool(dimensions="width")
    boxzoom.overlay.fill_color = "grey"
    boxzoom.overlay.fill_alpha = 0.1
    boxzoom.overlay.line_width = 0.5
    p.add_tools(hover)
    p.add_tools(boxzoom)

    molPlot = bokeh.models.Div(name="moldiv", text="""Structure""",
                               width=200, height=100)
    save(Row(p, molPlot), template=template)
    view("multiline.html")


if __name__ == "__main__":
    main()
