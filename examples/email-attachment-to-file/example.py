"""
Yandex mail -> simple .dat file

------ -- ------ COMMAND     naive run      ---------CONFIG SETUP---------------- SOURCE DESTINATION
python -m aftafa   run     --naive=False    --config="test-samples/pipeline.yaml" email  file
"""

from aftafa.common.pipeline import Pipeline, PipelineConfig

pipe_cfg = PipelineConfig("test-samples/pipeline.yaml")
p = Pipeline(pipeline_name='email-attachment-to-file', pipeline_config=pipe_cfg)
p.run(naive=False)
