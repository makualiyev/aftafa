# Pipeline configuration


```yaml
source:
  type: email
  attachment_only: true
  attachment_file_type_accept: "xls;xlsx;zip"
  config_file: "test-samples/imap_mail_config.json"
destination:
  type: file
  output_path: "test-samples"
  file_extension: "eml"
  transformer:
    jsonpath: "$.data"

```

