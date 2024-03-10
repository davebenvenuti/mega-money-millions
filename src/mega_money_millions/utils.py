def safe(object: any, path: str | list[str] | tuple[str]):
  if isinstance(path, str):
    path_parts = path.split('.')
  else:
    path_parts = path

  for part in path_parts:
    if hasattr(object, part):
      object = getattr(object, part)
    else:
      return None

  return object
