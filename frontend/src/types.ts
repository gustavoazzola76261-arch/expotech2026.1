export type UserRole = "professor" | "mestre" | "admin";

export type Me = {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  room_ids: number[];
};

export type Room = { id: number; name: string; code: string };

export type AirConditioner = {
  id: number;
  room_id: number;
  name: string;
  slot: number;
  power_watts: number;
  is_on: boolean;
  target_temp_c: number;
};

export type RoomOverview = Room & { lamps: Lamp[]; air_conditioners: AirConditioner[] };

export type ScheduleScope = "all" | "room" | "rooms_group" | "lamp" | "lamps_group";

export type LampSchedule = {
  id: number;
  name: string;
  scope: ScheduleScope;
  action: "on" | "off";
  hour: number;
  minute: number;
  room_id: number | null;
  lamp_id: number | null;
  room_ids: number[] | null;
  lamp_ids: number[] | null;
  days_of_week: number[] | null;
  days_label?: string | null;
  is_enabled: boolean;
  room_name?: string | null;
  lamp_name?: string | null;
  target_label?: string | null;
};

/** 0=segunda … 6=domingo */
export const WEEKDAYS = [
  { value: 0, label: "Segunda" },
  { value: 1, label: "Terça" },
  { value: 2, label: "Quarta" },
  { value: 3, label: "Quinta" },
  { value: 4, label: "Sexta" },
  { value: 5, label: "Sábado" },
  { value: 6, label: "Domingo" },
] as const;

export type Lamp = {
  id: number;
  room_id: number;
  name: string;
  slot: number;
  power_watts: number;
  is_on: boolean;
};

export type EnelTariffInfo = {
  distributor: string;
  tariff_group: string;
  te_brl_per_kwh: string;
  tusd_brl_per_kwh: string;
  bandeira_brl_per_kwh: string;
  icms_rate: string;
  pis_cofins_rate: string;
  unit_price_brl_per_kwh: string;
};

export type ConsumptionSummary = {
  total_kwh: string;
  total_brl: string;
  tariff: EnelTariffInfo;
};

export type ConsumptionMonthlyPoint = { year_month: string; kwh: string; brl: string };

export type IAInsightsResponse = {
  analysis: string;
  report: string;
  savings_suggestions: string[];
  waste_detection: string[];
  model: string;
  generated_at: string;
  months_window: number;
  room_id: number | null;
  operation_context_used?: string | null;
};

export type IALastReportResponse = {
  has_report: boolean;
  generated_at?: string | null;
  months_window?: number | null;
  room_id?: number | null;
  model?: string | null;
  operation_context_used?: string | null;
  analysis?: string | null;
  report?: string | null;
  savings_suggestions?: string[];
  waste_detection?: string[];
};

export type ConsumptionMonthlyResponse = {
  months_window: number;
  period_start: string;
  period_end: string;
  points: ConsumptionMonthlyPoint[];
  total_kwh_in_period: string;
  total_brl_in_period: string;
  tariff: EnelTariffInfo;
};

export type AdminUser = Me;

export type ActuationHistoryItem = {
  id: number;
  created_at: string;
  action: "on" | "off";
  energy_kwh: string | null;
  user_id: number | null;
  user_name: string | null;
  user_email: string | null;
  room_id: number;
  room_name: string;
  room_code: string;
  lamp_id: number;
  lamp_name: string;
  lamp_slot: number;
};
