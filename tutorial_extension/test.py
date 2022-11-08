import bokeh.models
import pyopenms as oms

import rdkit.Chem
from bokeh.embed import file_html
from bokeh.io import save
from bokeh.models import HoverTool, ColumnDataSource, BoxZoomTool, Row, CustomJS
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
            };
            setTimeout(initMol, 500);
        </script>
    {% endblock %}
    """

    # prepare some data

    mzs = [1., 2., 3.5, 4., 5.]
    itys = [6., 7., 2., 4., 5.]
    #annotList = ["", "Cc1cc(-n2ncc(=O)[nH]c2=O)cc(C)c1C(O)c1ccc(Cl)cc1", "", "", ""]
    annotList = ["", "Oc1[c,n]cccc1", "", "c1[c,n]cccc1", ""]

    #annotList = [mol2svg(i) for i in annotList]
    columns = ["mz", "ity", "annot"]

    # create a new plot with a title and axis labels
    p = figure(title="Simple line example", x_axis_label='m/z', y_axis_label='Intensity',
               tools=['xwheel_zoom', 'xpan'], active_scroll='xwheel_zoom')

    # add a line renderer with legend and line thickness to the plot
    i = 0
    for mz, ity, annot in zip(mzs, itys, annotList):
        source = ColumnDataSource(pd.DataFrame(
            {
                "mz": [mz, mz],
                "ity": [0, ity],
                "annot": ["", annot]
            }
        ))
        p.line(name="peak"+str(i), x="mz", y="ity", source=source, line_width=2, hover_line_width=3,
               color=("black" if annot == "" else "red"))
        i += 1

    js_code = """
    var annot = cb_data.renderer.data_source.data.annot[1]
    var peakstr = cb_data.renderer.name
    console.log(annot)
    console.log(peakstr)
    console.log(cb_data.index.indices.length)
    console.log(cb_data.index['1d'])
    if (annot != "" && isFinite(cb_data.geometry.x))
    {
        window.lastPeakStr = peakstr;
        var moldiv = Bokeh.documents[0].get_model_by_name('moldiv')
        var smiles = "CC(=O)Oc1ccccc1C(=O)O";
        var mol = RDKitModule.get_mol(smiles);
        var qmol = RDKitModule.get_qmol(annot);
        var mdetails = mol.get_substruct_match(qmol);
        moldiv.text = mol.get_svg_with_highlights(mdetails);
    } else if (window.lastPeakStr == peakstr && !isFinite(cb_data.geometry.x)){
        var moldiv = Bokeh.documents[0].get_model_by_name('moldiv')
        var smiles = "CC(=O)Oc1ccccc1C(=O)O";
        var mol = RDKitModule.get_mol(smiles);
        var qmol = RDKitModule.get_qmol(annot);
        moldiv.text = mol.get_svg();
    }
    """ % annotList

    #args={'smiles': cr.data_source, 'segment': sr.data_source}
    cb = CustomJS(code=js_code)
    hover = HoverTool(
        tooltips="""
                    <div>
                    <div>
                        @annot
                    <div>
                        <b>m/z:</b> <span style="font-size: 12px; color: #696;">@mz{0.000}</span><br>
                        <b>Intensity:</b> <span style="font-size: 12px; color: #796;">@ity{0.000}</span>
                    </div>
                </div>
                """,
        callback=cb
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
    save(Row(p,molPlot), template=template)
    view("test.html")


if __name__ == "__main__":
    main()
