{{/*
Declare the ".name" template to get the base name of the Helm Chart.
*/}}
{{- define ".name" -}}
  {{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}
