output "invoke_url" {
  value = "${aws_api_gateway_deployment.api_deployment.invoke_url}/${aws_api_gateway_resource.proxy.path_part}"
}