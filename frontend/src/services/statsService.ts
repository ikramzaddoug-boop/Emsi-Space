import API from "@/api";

export interface DashboardStats {
  total_rooms: number;
  available_rooms: number;
  total_equipments: number;
  total_reservations: number;
  total_users: number;
  occupation_rate: number;
  par_salle?: { name: string; count: number }[];
}

export interface ReservationStats {
  total: number;
  confirmees: number;
  en_attente: number;
  annulees: number;
  recent: any[];
}

export const getGlobalStats = async (): Promise<DashboardStats> => {
  const res = await API.get("/stats/");
  return res.data;
};

// Combined stats: merges room + equipment reservation counts for the logged-in user
export const getReservationStats = async (): Promise<ReservationStats> => {
  const res = await API.get("/reservations/rooms/statistiques/");
  return res.data;
};

// Pending reservations: fetch both room and equipment reservations filtered by status
export const getPendingReservations = async (limit = 5) => {
  const [rooms, equips] = await Promise.all([
    API.get("/reservations/rooms/", { params: { status: "en_attente" } }),
    API.get("/reservations/equipments/", { params: { status: "en_attente" } }),
  ]);
  const roomList = (rooms.data.results || rooms.data).map((r: any) => ({ ...r, res_type: "room" }));
  const equipList = (equips.data.results || equips.data).map((r: any) => ({ ...r, res_type: "equipment" }));
  return [...roomList, ...equipList]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, limit);
};

export const getPopularRooms = async (limit = 3) => {
  const res = await API.get(`/rooms/`, { params: { limit } });
  return res.data.results || res.data;
};
