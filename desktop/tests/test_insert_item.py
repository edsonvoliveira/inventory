from desktop.data.repositories.inventory_items_repo import insert_item

uuid = insert_item(
    zone_uuid="UUID-ZONA-TESTE",
    product_uuid="UUID-PRODUTO-TESTE",
    user_uuid="UUID-USER-TESTE",
    scanned_code="123456789",
    qty_counted=10
)

print(uuid)
