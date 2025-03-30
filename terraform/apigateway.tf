# Crear la API Gateway
resource "aws_api_gateway_rest_api" "api_proxy_api" {
  name        = "api-proxy-api"
  description = "API Gateway para proxy de solicitudes a Mercado Libre"
}

# Crear un recurso para la ruta proxy (permitiendo cualquier ruta después de la raíz)
resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.api_proxy_api.id
  parent_id   = aws_api_gateway_rest_api.api_proxy_api.root_resource_id
  path_part   = "{proxy+}"
}

# Crear el método ANY para el recurso proxy
resource "aws_api_gateway_method" "proxy_method" {
  rest_api_id   = aws_api_gateway_rest_api.api_proxy_api.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "NONE" # Puedes cambiar esto a otro tipo de autorización si lo necesitas
}

# Integrar el método ANY con la función Lambda
resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api_proxy_api.id
  resource_id             = aws_api_gateway_resource.proxy.id
  http_method             = aws_api_gateway_method.proxy_method.http_method
  integration_http_method = "POST" # API Gateway usa POST para invocar Lambdas con AWS_PROXY
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.api_proxy_lambda.invoke_arn
}

# Crear la implementación (deployment) de la API Gateway
resource "aws_api_gateway_deployment" "api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.api_proxy_api.id
  depends_on = [
    aws_api_gateway_integration.lambda_integration,
  ]
}

# Permitir que API Gateway invoque la función Lambda
resource "aws_lambda_permission" "api_gateway_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_proxy_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn = "${aws_api_gateway_rest_api.api_proxy_api.execution_arn}/*/*"
}