import type { ReactNode } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "./components/Layout";
import { ActuationHistoryPage } from "./pages/ActuationHistoryPage";
import { AdminUsersPage } from "./pages/AdminUsersPage";
import { DashboardPage } from "./pages/DashboardPage";
import { LoginPage } from "./pages/LoginPage";
import { AiInsightsPage } from "./pages/AiInsightsPage";
import { ReportsPage } from "./pages/ReportsPage";
import { RoomPage } from "./pages/RoomPage";
import { RoomsManagePage } from "./pages/RoomsManagePage";
import { SchedulesPage } from "./pages/SchedulesPage";
import { getToken } from "./api/client";

const qc = new QueryClient();

function Protected({ children }: { children: ReactNode }) {
  if (!getToken()) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export function App() {
  return (
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <Protected>
                <Layout />
              </Protected>
            }
          >
            <Route index element={<DashboardPage />} />
            <Route path="salas/:roomId" element={<RoomPage />} />
            <Route path="relatorios" element={<ReportsPage />} />
            <Route path="ia" element={<AiInsightsPage />} />
            <Route path="admin/usuarios" element={<AdminUsersPage />} />
            <Route path="admin/historico" element={<ActuationHistoryPage />} />
            <Route path="admin/salas" element={<RoomsManagePage />} />
            <Route path="programacao" element={<SchedulesPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
