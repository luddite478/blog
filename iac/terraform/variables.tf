locals {
  env_vars = {
    for tuple in regexall("(.*?)=(.*)", file("../.infra.env")) :
    tuple[0] => replace(replace(tuple[1], "/\"/", ""), "/\\r$/", "")
  }
}