import logging
import knime_extension as knext
import pyopenms as oms

import rdkit.Chem
from bokeh.embed import file_html
from bokeh.models import HoverTool, ColumnDataSource, BoxZoomTool
from bokeh.resources import CDN
from rdkit.Chem.Draw import rdMolDraw2D
from bokeh.plotting import figure, show
import pandas as pd


def mol2svg(smiles):
    if smiles == "":
        return ""
    mol = rdkit.Chem.MolFromSmiles(smiles)
    d2d = rdMolDraw2D.MolDraw2DSVG(200, 100)
    d2d.DrawMolecule(mol)
    d2d.FinishDrawing()
    return d2d.GetDrawingText()




LOGGER = logging.getLogger(__name__)


@knext.node(name="My Template Node", node_type=knext.NodeType.LEARNER, icon_path="icon.png", category="/")
@knext.input_table(name="Input Data", description="We read data from here")
# @knext.input_table(name="Tutorial: Input Data 2", description="We also read data from here") ### Tutorial step 11: Uncomment to create a new input port
@knext.output_table(name="Output Data", description="Whatever the node has produced")
@knext.output_view(name="My pretty view", description="Showing a seaborn plot")
class TemplateNode:
    """

    This node has a description
    """

    ### Tutorial step 10: Uncomment all of the following parameters and the 'is_numeric' method to create your first dialogue ###
    # (Restart KAP and drag&drop the node again from the node repository to let changes take effect)
    # some_param = knext.IntParameter("Some Int Parameter", "The answer to everything", 42, min_value=0)

    # another_param = knext.StringParameter("Some String parameter", "The classic placeholder", "foobar")

    # double_param = knext.DoubleParameter("Double Parameter", "Just for test purposes", 3.0)

    # boolean_param = knext.BoolParameter("Boolean Parameter", "also just for testing", True)

    # column_param = knext.ColumnParameter()

    # def is_numeric(column):  # Filter columns visible in the column_param for numeric ones
    #     return (
    #         column.ktype == knext.double()
    #         or column.ktype == knext.int32()
    #         or column.ktype == knext.int64()
    #     )

    # column_param = knext.ColumnParameter(label="label", description="description", port_index=0, column_filter=is_numeric)

    def configure(self, configure_context, input_schema_1):
    # def configure(self, configure_context, input_schema_1, input_schema_2):  ### Tutorial step 11: Uncomment to configure the new port (and comment out the previous configure header)
        return input_schema_1
        ### Tutorial step 12: Uncomment the following to adjust to the changes we do in this step in the execute method (and comment out the previous return statement)
        # return input_schema_1.append(knext.Column(knext.double(), "column2"))
        ### Tutorial step 13: Uncomment to set a warning for the configuration, which will be shown in the workflow
        # configure_context.set_warning("This is a warning during configuration")

 
    def execute(self, exec_context, input_1):
    # def execute(self, exec_context, input_1, input_2):  ### Tutorial step 11: Uncomment to accept the new port (and comment out the previous execute header)
        input_1_pandas = input_1.to_pandas()
        aaseq = oms.AASequence.fromString("DFPIANGER")
        input_1_pandas["column1"][0] = aaseq.getMonoWeight()

        # prepare some data
        mzs = [1., 2., 3.5, 4., 5.]
        itys = [6., 7., 2., 4., 5.]
        annotList = ["", "Cc1cc(-n2ncc(=O)[nH]c2=O)cc(C)c1C(O)c1ccc(Cl)cc1", "", "", ""]
        annotList = [mol2svg(i) for i in annotList]
        columns = ["mz", "ity", "annot"]

        # create a new plot with a title and axis labels
        p = figure(title="Simple line example", x_axis_label='m/z', y_axis_label='Intensity',
                   tools=['xwheel_zoom', 'xpan'], active_scroll='xwheel_zoom')

        # add a line renderer with legend and line thickness to the plot
        for mz, ity, annot in zip(mzs, itys, annotList):
            source = ColumnDataSource(pd.DataFrame(
                {
                    "mz": [mz, mz],
                    "ity": [0, ity],
                    "annot": ["", annot]
                }
            ))
            p.line(x="mz", y="ity", source=source, line_width=2, hover_line_width=3,
                   color=("black" if annot == "" else "red"))

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
        )

        hover.line_policy = 'next'
        boxzoom = BoxZoomTool(dimensions="width")
        boxzoom.overlay.fill_color = "grey"
        boxzoom.overlay.fill_alpha = 0.1
        boxzoom.overlay.line_width = 0.5
        p.add_tools(hover)
        p.add_tools(boxzoom)

        html = file_html(p, CDN)
        return knext.Table.from_pandas(input_1_pandas), knext.view_html(html)
        ### Tutorial step 12: Uncomment the following lines to work with the new port (and comment out the previous return statement)
        # input_1_pandas = input_1.to_pandas() # Transform the input table to some processable format (pandas or pyarrow)
        # input_2_pandas = input_2.to_pandas()
        # input_1_pandas['column2'] = input_1_pandas['column1'] + input_2_pandas['column1']
        # return knext.Table.from_pandas(input_1_pandas)
        ### Tutorial step 13: Uncomment the following line to use the parameters from the configuration dialogue (and comment out the previous return statement)
        # input_1_pandas['column2'] = input_1_pandas['column2'] + self.double_param
        # LOGGER.warning(self.double_param) # Tutorial step 14: Logging some warning to the console
        # exec_context.set_warning("This is a warning") # Tutorial step 14: Set a warning to be shown in the workflow
        # return knext.Table.from_pandas(input_1_pandas) ### Tutorial step 13: Uncomment
