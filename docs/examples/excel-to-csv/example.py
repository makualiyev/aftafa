"""
Excel file as dataframes -> simple .csv file

------ -- ------ COMMAND     naive run      ---------CONFIG SETUP---------------- SOURCE DESTINATION
python -m aftafa   run     --naive=True    --config="test-samples/xl-to-csv.yaml" excel  file
"""

from aftafa.common.pipeline import Pipeline, PipelineConfig

pipe_cfg = PipelineConfig("docs/examples/excel-to-csv/pipeline.yaml")
p = Pipeline(pipeline_name='excel-to-csv', pipeline_config=pipe_cfg)
p.run(naive=True)
