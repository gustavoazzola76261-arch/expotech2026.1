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

export type Lamp = {
  id: number;
  room_id: number;
  name: string;
  slot: number;
  power_watts: number;
  is_on: boolean;
};

export type ConsumptionSummary = { total_kwh: string };

export type ConsumptionMonthlyPoint = { year_month: string; kwh: string };

export type ConsumptionMonthlyResponse = {
  months_window: number;
  period_start: string;
  period_end: string;
  points: ConsumptionMonthlyPoint[];
  total_kwh_in_period: string;
};

export type AdminUser = Me;
