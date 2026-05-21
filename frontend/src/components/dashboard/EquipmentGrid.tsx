import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Modal } from "./Modal";
import { getEquipments } from "../../services/equipmentService";
import { createEquipmentReservation, checkEquipmentAIConflict } from "../../services/reservationService";
import { useToast } from "./Toast";
import { FiSearch, FiBox, FiClock, FiCpu, FiInfo, FiAlertTriangle, FiCheck } from "react-icons/fi";

export function EquipmentGrid() {
  const toast = useToast();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<any>(null);
  const [reserveOpen, setReserveOpen] = useState(false);
  
  const [date, setDate] = useState("");
  const [start, setStart] = useState("09:00");
  const [end, setEnd] = useState("10:00");
  const [purpose, setPurpose] = useState("");
  const [quantite, setQuantite] = useState(1);

  const [aiResult, setAiResult] = useState<any>(null);
  const [checkingAi, setCheckingAi] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const { data: equipment, isLoading } = useQuery({
    queryKey: ["equipment-list"],
    queryFn: () => getEquipments(),
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
          const res = await checkEquipmentAIConflict({ equipment: selected.id, date, heure_debut: start, heure_fin: end });
          setAiResult(res);
        } catch (e) { console.error(e); } finally { setCheckingAi(false); }
      }, 500);
      return () => clearTimeout(timer);
    } else { setAiResult(null); }
  }, [selected, date, start, end, validationError]);

  const reservationMutation = useMutation({
    mutationFn: (newRes: any) => createEquipmentReservation(newRes),
    onSuccess: () => {
      toast.push({ type: "success", msg: "Demande envoyée !" });
      setReserveOpen(false);
      setSelected(null);
      queryClient.invalidateQueries({ queryKey: ["my-reservation-stats"] });
    },
    onError: (err: any) => toast.push({ type: "error", msg: err.response?.data?.error || err.response?.data?.non_field_errors?.[0] || "Erreur" })
  });

  const filtered = (equipment || []).filter((e: any) =>
    e.name.toLowerCase().includes(search.toLowerCase()) && e.is_available
  );

  const handleReserve = () => {
    if (validationError || !date || !start || !end) return;
    reservationMutation.mutate({
      equipment: selected.id,
      date,
      heure_debut: start,
      heure_fin: end,
      titre: purpose || "Réservation matériel",
      description: purpose,
      quantite: quantite
    });
  };

  return (
    <div className="space-y-6">
      <div className="card-elev p-4 flex flex-wrap gap-3 items-center">
        <div className="relative flex-1 min-w-[200px]">
          <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-gray-400" />
          <input className="input-field pl-10" placeholder="Rechercher un équipement..." value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 animate-pulse">
           {[1,2,3,4].map(i => <div key={i} className="h-64 bg-gray-50 rounded-2xl" />)}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {filtered.map((e: any) => (
            <div key={e.id} className="card-elev group cursor-pointer hover:border-blue-500 transition-all hover:shadow-lg" onClick={() => setSelected(e)}>
              <div className="aspect-square bg-gray-50 rounded-2xl mb-4 flex items-center justify-center relative overflow-hidden group-hover:bg-blue-50/50">
                 {e.photo_url ? (
                   <img src={e.photo_url} className="size-full object-cover rounded-2xl transition-transform group-hover:scale-110" />
                 ) : (
                   <FiBox className="size-12 text-gray-200 group-hover:text-blue-200" />
                 )}
                 <span className="absolute top-3 right-3 badge badge-success shadow-lg shadow-green-200">En stock</span>
              </div>
              <h3 className="font-bold text-gray-900 group-hover:text-blue-600 transition-colors">{e.name}</h3>
              <p className="text-[10px] text-gray-400 font-bold uppercase mt-1">Stock total: {e.quantity}</p>
            </div>
          ))}
        </div>
      )}

      <Modal open={reserveOpen} onClose={() => setReserveOpen(false)} title="Réserver ce matériel">
        <div className="space-y-4">
          <div className="p-3 bg-blue-50 rounded-xl border border-blue-100 flex items-center gap-2 text-blue-700 text-xs font-semibold">
             <FiInfo className="size-4 shrink-0" /> Vérifiez les dates, heures et la quantité nécessaires.
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-bold text-gray-400 uppercase">Date</label>
              <input type="date" className={`input-field mt-1 ${validationError?.includes("date") ? "border-red-500 bg-red-50" : ""}`} value={date} onChange={(e) => setDate(e.target.value)} />
            </div>
            <div>
              <label className="text-xs font-bold text-gray-400 uppercase">Quantité</label>
              <input type="number" min="1" max={selected?.quantity || 1} className="input-field mt-1" value={quantite} onChange={(e) => setQuantite(parseInt(e.target.value) || 1)} />
            </div>
            <div className="grid grid-cols-2 gap-2 md:col-span-2">
              <div><label className="text-xs font-bold text-gray-400 uppercase">Début</label><input type="time" className="input-field mt-1" value={start} onChange={(e) => setStart(e.target.value)} /></div>
              <div><label className="text-xs font-bold text-gray-400 uppercase">Fin</label><input type="time" className={`input-field mt-1 ${validationError?.includes("time") ? "border-red-500 bg-red-50" : ""}`} value={end} onChange={(e) => setEnd(e.target.value)} /></div>
            </div>
          </div>
          {validationError && <div className="p-3 bg-red-50 text-red-600 text-xs font-bold rounded-xl">{validationError}</div>}
          
          {aiResult?.has_conflict && (
            <div className="p-4 bg-orange-50 rounded-xl border border-orange-100 animate-fade-in">
              <div className="flex items-center gap-2 text-orange-700 font-bold text-sm">
                <FiAlertTriangle /> Stock insuffisant pour ce créneau.
              </div>
              <p className="text-xs text-orange-600 mt-1">Il ne reste que <strong>{aiResult.available_stock}</strong> article(s) disponible(s) à ces horaires.</p>
            </div>
          )}

          <button className="btn-primary w-full py-4 mt-2 disabled:opacity-50" onClick={handleReserve} disabled={reservationMutation.isPending || !!validationError || !date || aiResult?.has_conflict}>
            {reservationMutation.isPending ? "Traitement..." : "Confirmer la réservation"}
          </button>
        </div>
      </Modal>

      <Modal open={!!selected && !reserveOpen} onClose={() => setSelected(null)} title={selected?.name}>
         <div className="space-y-6 text-center">
            <div className="aspect-square bg-gray-50 rounded-2xl flex items-center justify-center overflow-hidden">
               {selected?.photo_url ? <img src={selected?.photo_url} className="size-full object-cover" /> : <FiBox className="size-20 text-gray-200" />}
            </div>
            <button className="btn-primary w-full py-4 shadow-xl shadow-blue-500/20" onClick={() => setReserveOpen(true)}>Continuer la réservation</button>
         </div>
      </Modal>
    </div>
  );
}
