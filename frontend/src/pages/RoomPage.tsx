import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { apiFetch } from "../api/client";
import { RoomFloorPlan } from "../components/RoomFloorPlan";
import type { AirConditioner, Lamp, Me, Room } from "../types";

async function fetchLamps(roomId: string): Promise<Lamp[]> {
  return apiFetch<Lamp[]>(`/api/v1/rooms/${roomId}/lamps`);
}

async function fetchAcUnits(roomId: string): Promise<AirConditioner[]> {
  return apiFetch<AirConditioner[]>(`/api/v1/rooms/${roomId}/ac`);
}

async function fetchRooms(): Promise<Room[]> {
  return apiFetch<Room[]>("/api/v1/rooms");
}

export function RoomPage() {
  const { roomId } = useParams();
  const qc = useQueryClient();
  const id = roomId ?? "";

  const { data: me } = useQuery({
    queryKey: ["me"],
    queryFn: () => apiFetch<Me>("/api/v1/me"),
  });
  const { data: rooms } = useQuery({ queryKey: ["rooms"], queryFn: fetchRooms });
  const { data, isLoading, error } = useQuery({
    queryKey: ["lamps", id],
    queryFn: () => fetchLamps(id),
    enabled: Boolean(id),
  });
  const {
    data: acUnits,
    isLoading: loadingAc,
    error: acError,
  } = useQuery({
    queryKey: ["ac", id],
    queryFn: () => fetchAcUnits(id),
    enabled: Boolean(id),
  });

  const mutation = useMutation({
    mutationFn: async ({ lampId, action }: { lampId: number; action: "on" | "off" }) => {
      return apiFetch<Lamp>(`/api/v1/lamps/${lampId}/command`, {
        method: "POST",
        json: { action },
      });
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["lamps", id] }),
  });

  const acMutation = useMutation({
    mutationFn: async ({ acId, action }: { acId: number; action: "on" | "off" }) =>
      apiFetch<AirConditioner>(`/api/v1/ac/${acId}/command`, {
        method: "POST",
        json: { action },
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["ac", id] });
      qc.invalidateQueries({ queryKey: ["rooms-overview"] });
    },
  });

  const acTempMutation = useMutation({
    mutationFn: async ({ acId, target_temp_c }: { acId: number; target_temp_c: number }) =>
      apiFetch<AirConditioner>(`/api/v1/ac/${acId}/temperature`, {
        method: "PATCH",
        json: { target_temp_c },
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["ac", id] });
      qc.invalidateQueries({ queryKey: ["rooms-overview"] });
    },
  });

  const roomTitle = rooms?.find((r) => String(r.id) === id)?.name;
  const canSetTemp = me?.role === "admin" || me?.role === "mestre";
  const busy = mutation.isPending || acMutation.isPending || acTempMutation.isPending;

  function toggleLamp(lamp: Lamp) {
    const action = lamp.is_on ? "off" : "on";
    mutation.mutate({ lampId: lamp.id, action });
  }

  function toggleAc(unit: AirConditioner) {
    acMutation.mutate({ acId: unit.id, action: unit.is_on ? "off" : "on" });
  }

  if (!id) return null;
  if (isLoading || loadingAc) return <p className="muted">Carregando sala…</p>;
  if (error) return <p className="error-banner">{(error as Error).message}</p>;
  if (acError) return <p className="error-banner">{(acError as Error).message}</p>;

  const hasDevices = (data?.length ?? 0) > 0 || (acUnits?.length ?? 0) > 0;

  return (
    <div className="room-page">
      {me?.role !== "professor" && (
        <Link to="/" className="back-link">
          ← Voltar às salas
        </Link>
      )}
      <h2>{roomTitle ?? `Sala #${id}`}</h2>
      <p className="muted room-page-hint">
        Clique nas lâmpadas ou nos aparelhos de ar (lado direito) para ligar ou desligar.
        {canSetTemp ? " Mestre e admin podem ajustar a temperatura de cada aparelho." : ""}
      </p>

      {hasDevices ? (
        <RoomFloorPlan
          lamps={data ?? []}
          airConditioners={acUnits ?? []}
          disabled={busy}
          acDisabled={busy}
          canSetTemp={canSetTemp}
          onToggle={toggleLamp}
          onAcToggle={toggleAc}
          onAcTempChange={(unit, temp) => acTempMutation.mutate({ acId: unit.id, target_temp_c: temp })}
        />
      ) : (
        <p className="muted">Nenhuma lâmpada nem ar-condicionado cadastrado nesta sala.</p>
      )}

      {(acMutation.error || acTempMutation.error) && (
        <div className="error-banner">
          {((acMutation.error || acTempMutation.error) as Error).message}
        </div>
      )}
    </div>
  );
}
