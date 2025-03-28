"""
REST API Json response -> simple .json file

------ -- ------ COMMAND     naive run      ---------CONFIG SETUP---------------- SOURCE DESTINATION
python -m aftafa   run     --naive=False    --config="test-samples/rest-to-json.yaml" restapi  file
"""

from aftafa.common.pipeline import Pipeline, PipelineConfig

pipe_cfg = PipelineConfig("docs/examples/rest-api-to-rawfile/pipeline_v2.yaml")
p = Pipeline(pipeline_name='restapi-to-json', pipeline_config=pipe_cfg)
p.run(naive=False)
