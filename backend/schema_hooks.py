import re

def flatten_paths(result, generator, request, public):
    for path in list(result['paths'].keys()):
        if '{tenant}' in path:
            # Create a normalized path without {tenant}
            normalized_path = path.replace('{tenant}/', '')
            result['paths'][normalized_path] = result['paths'][path]
            del result['paths'][path]
    return result

def flatten_id_folders(result, generator, request, public):
    """
    Flattens API endpoints by grouping all operations under a single folder per resource type.
    Removes unnecessary ID-based subfolders.
    """
    for path, path_item in result['paths'].items():
        for method, operation in path_item.items():
            if 'tags' in operation:
                # Flatten tags to avoid "id"-based subfolders
                operation['tags'] = [
                    tag.replace(" Id", "").replace("Id ", "").strip() for tag in operation['tags']
                ]
    return result




def clean_operation_ids(result, generator, request, public):
    """
    Simplifies operationId for all API endpoints in the OpenAPI schema.
    """
    for path, path_item in result['paths'].items():
        for method, operation in path_item.items():
            # Generate a clean name based on the path and method
            if 'operationId' in operation:
                original_id = operation['operationId']
                # Remove "api_", "_create", etc., and title-case the name
                cleaned_id = re.sub(r'(api_|_create|_update|_list|_retrieve|_destroy|_partial)', '', original_id)
                cleaned_id = cleaned_id.replace('_', ' ').title()  # Format to title case
                operation['operationId'] = cleaned_id.strip()
    return result


PUBLIC_API_ENDPOINTS = [
    "/api/login/"
    
]
def remove_security_for_public_api(result, generator, request, public):
    for path, path_item in result['paths'].items():
        for method, operation in path_item.items():

            # Remove security for public APIs
            if path in PUBLIC_API_ENDPOINTS:
                operation.pop('security', None)
    return result


