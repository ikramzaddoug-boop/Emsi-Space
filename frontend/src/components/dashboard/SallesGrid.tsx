import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Modal } from "./Modal";
import { getRooms } from "../../services/roomService";
import { createRoomReservation, checkRoomAIConflict } from "../../services/reservationService";
import { useToast } from "./Toast";
import { FiSearch, FiUsers, FiMapPin, FiClock, FiAlertTriangle, FiCheck, FiInfo, FiHome } from "react-icons/fi";

export function SallesGrid({ allowReserve = true }: { allowReserve?: boolean }) {
  const toast = useToast();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");
  const [selected, setSelected] = useState<any>(null);
  const [reserveOpen, setReserveOpen] = useState(false);
  
  const [date, setDate] = useState("");
  const [start, setStart] = useState("09:00");
  const [end, setEnd] = useState("10:00");
  const [purpose, setPurpose] = useState("");

  const [aiResult, setAiResult] = useState<any>(null);
  const [checkingAi, setCheckingAi] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const { data: rooms, isLoading } = useQuery({
    queryKey: ["rooms"],
    queryFn: () => getRooms(),
  });

  // Validation
  useEffect(() => {
    setValidationError(null);
    if (date) {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      if (new Date(date) < today) {
        setValidationError("The selected date is invalid. Please choose today or a future date.");
        return;
      }
    }
    if (start && end && start >= end) {
      setValidationError("The end time must be later than the start time.");
    }
  }, [date, start, end]);

  // IA
  useEffect(() => {
    if (selected && date && start && end && !validationError) {
      const timer = setTimeout(async () => {
        setCheckingAi(true);
        try {
          const res = await checkRoomAIConflict({ room: selected.id, date, heure_debut: start, heure_fin: end });
          setAiResult(res);
        } catch (e) { console.error(e); } finally { setCheckingAi(false); }
      }, 500);
      return () => clearTimeout(timer);
    } else { setAiResult(null); }
  }, [selected, date, start, end, validationError]);

  const reservationMutation = useMutation({
    mutationFn: (newRes: any) => createRoomReservation(newRes),
    onSuccess: () => {
      toast.push({ type: "success", msg: "Demande envoyée !" });
      setReserveOpen(false);
      setSelected(null);
      queryClient.invalidateQueries({ queryKey: ["rooms"] });
    },
    onError: (err: any) => toast.push({ type: "error", msg: err.response?.data?.error || "Erreur" })
  });

  const filtered = (rooms || []).filter((s: any) =>
    s.is_available === true && 
    s.name.toLowerCase().includes(search.toLowerCase()) &&
    (filter === "all" || (filter === "available" && s.is_available))
  );

  const handleReserve = () => {
    if (validationError || !date || !start || !end) return;
    reservationMutation.mutate({
      room: selected.id,
      date,
      heure_debut: start,
      heure_fin: end,
      titre: purpose || "Réservation",
      description: purpose,
      nombre_personnes: 1
    });
  };

  return (
    <>
      <div className="card-elev p-4 mb-4 flex flex-wrap gap-3 items-center">
        <div className="relative flex-1 min-w-[200px]">
          <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-gray-400" />
          <input className="input-field pl-10" placeholder="Rechercher une salle..." value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 animate-pulse">
           {[1,2,3].map(i => <div key={i} className="h-64 bg-gray-50 rounded-2xl" />)}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {filtered.map((s: any) => (
            <div key={s.id} className="card-elev group cursor-pointer hover:border-blue-500 transition-all hover:shadow-xl" onClick={() => setSelected(s)}>
              <div className="aspect-video relative overflow-hidden rounded-xl mb-4">
                <img src={s.image_url || "https://images.unsplash.com/photo-1497366754035-f200968a6e72"} alt="" className="size-full object-cover transition-transform group-hover:scale-105" />
                <span className="absolute top-2 right-2 badge badge-success">Libre</span>
              </div>
              <div className="flex justify-between items-center">
                <h3 className="font-bold text-lg">{s.name}</h3>
                <span className="text-[10px] uppercase font-bold text-blue-500 bg-blue-50 px-2 py-1 rounded">{s.room_type}</span>
              </div>
              <div className="flex items-center gap-3 text-xs text-gray-400 mt-2 font-medium">
                <span className="flex items-center gap-1"><FiMapPin className="size-3" />{s.location}</span>
                <span className="flex items-center gap-1"><FiUsers className="size-3" />{s.capacity} places</span>
              </div>
            </div>
          ))}
          {filtered.length === 0 && <div className="col-span-full py-20 text-center text-gray-400 font-medium">Aucune salle disponible.</div>}
        </div>
      )}

      <Modal open={reserveOpen} onClose={() => setReserveOpen(false)} title="Réserver cette salle">
        <div className="space-y-4">
          <div className="p-3 bg-blue-50 rounded-xl border border-blue-100 flex items-center gap-2 text-blue-700 text-xs font-semibold">
             <FiInfo className="size-4 shrink-0" /> Please review the date and time carefully.
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-bold text-gray-400 uppercase">Date</label>
              <input type="date" className={`input-field mt-1 ${validationError?.includes("date") ? "border-red-500 bg-red-50" : ""}`} value={date} onChange={(e) => setDate(e.target.value)} />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div><label className="text-xs font-bold text-gray-400 uppercase">Début</label><input type="time" className="input-field mt-1" value={start} onChange={(e) => setStart(e.target.value)} /></div>
              <div><label className="text-xs font-bold text-gray-400 uppercase">Fin</label><input type="time" className={`input-field mt-1 ${validationError?.includes("time") ? "border-red-500 bg-red-50" : ""}`} value={end} onChange={(e) => setEnd(e.target.value)} /></div>
            </div>
          </div>
          {validationError && <div className="p-3 bg-red-50 text-red-600 text-xs font-bold rounded-xl">{validationError}</div>}
          
          {aiResult?.has_conflict && (
            <div className="p-4 bg-orange-50 rounded-xl border border-orange-100 animate-fade-in">
              <div className="flex items-center gap-2 text-orange-700 font-bold mb-2 text-sm">
                <FiAlertTriangle /> Salle indisponible sur ce créneau.
              </div>
              {aiResult.suggestions?.length > 0 && (
                <div className="mt-2">
                  <p className="text-xs text-orange-600 mb-2 font-medium">Autres suggestions horaires :</p>
                  <div className="flex flex-wrap gap-2">
                    {aiResult.suggestions.map((s: any, i: number) => (
                      <button 
                        key={i} 
                        onClick={() => { setStart(s.start); setEnd(s.end); }}
                        className="px-3 py-1.5 bg-white border border-orange-200 text-orange-700 text-xs font-bold rounded-lg hover:bg-orange-100 transition-colors shadow-sm"
                      >
                        {s.start} - {s.end}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          <button className="btn-primary w-full py-4 mt-2 disabled:opacity-50" onClick={handleReserve} disabled={reservationMutation.isPending || !!validationError || !date || aiResult?.has_conflict}>
            {reservationMutation.isPending ? "Traitement..." : "Confirmer la réservation"}
          </button>
        </div>
      </Modal>

      <Modal open={!!selected && !reserveOpen} onClose={() => setSelected(null)} title={selected?.name}>
         <div className="space-y-6 text-center">
            <div className="aspect-video bg-gray-100 rounded-2xl overflow-hidden shadow-inner"><img src={selected?.image_url} className="size-full object-cover" /></div>
            <button className="btn-primary w-full py-4" onClick={() => setReserveOpen(true)}>Continuer vers la réservation</button>
         </div>
      </Modal>
    </>
  );
}
