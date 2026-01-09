from desktop.data.repositories.zone_user_progress_repo import start_zone, finish_zone

p_uuid = start_zone(
    zone_uuid="UUID-ZONA-TESTE",
    user_uuid="UUID-USER-TESTE"
)

finish_zone(progress_uuid=p_uuid)
