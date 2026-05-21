import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { PageHeader } from "@/components/dashboard/PageHeader";
import { Modal } from "@/components/dashboard/Modal";
import { getEquipments, updateEquipment, deleteEquipment, createEquipment } from "@/services/equipmentService";
import { useToast } from "@/components/dashboard/Toast";
import { FiPlus, FiEdit2, FiTrash2, FiSearch, FiBox } from "react-icons/fi";

export const Route = createFileRoute("/admin/equipment")({ component: AdminEquipment });

function AdminEquipment() {
  const toast = useToast();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingEq, setEditingEq] = useState<any>(null);

  const { data: equipment, isLoading } = useQuery({
    queryKey: ["admin-equipment"],
    queryFn: () => getEquipments(),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteEquipment(id),
    onSuccess: () => {
      toast.push({ type: "success", msg: "Matériel supprimé" });
      queryClient.invalidateQueries({ queryKey: ["admin-equipment"] });
      queryClient.invalidateQueries({ queryKey: ["global-stats"] });
    }
  });

  const saveMutation = useMutation({
    mutationFn: (data: any) => editingEq?.id ? updateEquipment(editingEq.id, data) : createEquipment(data),
    onSuccess: () => {
      toast.push({ type: "success", msg: editingEq?.id ? "Matériel mis à jour" : "Matériel créé" });
      setIsModalOpen(false);
      setEditingEq(null);
      queryClient.invalidateQueries({ queryKey: ["admin-equipment"] });
      queryClient.invalidateQueries({ queryKey: ["global-stats"] });
    },
    onError: (err: any) => {
      const detail = err?.response?.data;
      const msg = typeof detail === 'object'
        ? Object.entries(detail).map(([k, v]) => `${k}: ${v}`).join(' | ')
        : "Erreur lors de la création";
      toast.push({ type: "error", msg });
    }
  });

  const filtered = (equipment || []).filter((e: any) => 
    e.name.toLowerCase().includes(search.toLowerCase()) || 
    e.description?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-6">
      <div className="flex justify-between items-end mb-6">
        <PageHeader title="Gestion du Matériel" subtitle="Gérez le stock d'équipements disponibles." />
        <button 
          onClick={() => { setEditingEq(null); setIsModalOpen(true); }}
          className="btn-primary flex items-center gap-2"
        >
          <FiPlus /> Nouvel Équipement
        </button>
      </div>

      <div className="card-elev p-4 mb-6 flex items-center gap-4">
        <div className="relative flex-1">
          <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input 
            type="text" 
            placeholder="Rechercher un équipement..." 
            className="input-field pl-10"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {isLoading ? (
          <div className="col-span-full py-20 text-center text-muted-foreground">Chargement...</div>
        ) : filtered.length > 0 ? (
          filtered.map((item: any) => (
            <div key={item.id} className="card-elev group p-4 flex flex-col gap-4 relative overflow-hidden">
              <div className="aspect-square rounded-xl bg-white/5 border border-white/5 overflow-hidden">
                {item.photo_url ? (
                  <img src={item.photo_url} alt={item.name} className="size-full object-cover" />
                ) : (
                  <div className="size-full flex items-center justify-center text-muted-foreground/20">
                    <FiBox className="size-12" />
                  </div>
                )}
              </div>
              <div>
                <h3 className="font-bold">{item.name}</h3>
                <p className="text-xs text-muted-foreground mt-1 line-clamp-2 min-h-[32px]">{item.description || "Aucune description"}</p>
                <div className="flex items-center justify-between mt-4">
                  <span className="text-sm font-bold bg-primary/20 text-primary px-2 py-1 rounded-md">Stock: {item.quantity}</span>
                  <div className={`text-[10px] uppercase font-bold ${item.is_available ? 'text-success' : 'text-destructive'}`}>
                    {item.is_available ? 'Disponible' : 'Indisponible'}
                  </div>
                </div>
              </div>
              <div className="flex gap-2 mt-2 pt-4 border-t border-white/5">
                <button 
                  onClick={() => { setEditingEq(item); setIsModalOpen(true); }}
                  className="btn-secondary flex-1 py-2 text-xs flex items-center justify-center gap-2"
                >
                  <FiEdit2 className="size-3" /> Modifier
                </button>
                <button 
                  onClick={() => { if(confirm("Supprimer cet équipement ?")) deleteMutation.mutate(item.id); }}
                  className="btn-secondary flex-1 py-2 text-xs text-destructive hover:bg-destructive/10 hover:border-destructive/20 flex items-center justify-center gap-2"
                >
                  <FiTrash2 className="size-3" /> Supprimer
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-full py-20 text-center text-muted-foreground">Aucun équipement trouvé.</div>
        )}
      </div>

      <Modal 
        open={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        title={editingEq ? "Modifier l'Équipement" : "Ajouter un Équipement"}
      >
        <form 
          className="space-y-4"
          onSubmit={(e) => {
            e.preventDefault();
            const formData = new FormData(e.currentTarget);
            const data = Object.fromEntries(formData.entries());
            saveMutation.mutate({
              name: data.name,
              description: (data.description as string).trim() || null,
              photo_url: (data.photo_url as string).trim() || null,
              quantity: parseInt(data.quantity as string) || 1,
              is_available: data.is_available === 'on'
            });
          }}
        >
          <div>
            <label className="text-sm font-medium">Nom de l'équipement</label>
            <input name="name" defaultValue={editingEq?.name} className="input-field mt-1" required />
          </div>
          <div>
            <label className="text-sm font-medium">Description</label>
            <textarea name="description" defaultValue={editingEq?.description} className="input-field mt-1" rows={3} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium">Quantité totale</label>
              <input name="quantity" type="number" defaultValue={editingEq?.quantity || 1} className="input-field mt-1" required />
            </div>
            <div>
              <label className="text-sm font-medium">Photo URL</label>
              <input name="photo_url" defaultValue={editingEq?.photo_url} className="input-field mt-1" placeholder="https://..." maxLength={500} />
            </div>
          </div>
          <div className="flex items-center gap-2 pt-2">
            <input type="checkbox" name="is_available" defaultChecked={editingEq ? editingEq.is_available : true} id="is_available_eq" />
            <label htmlFor="is_available_eq" className="text-sm">Disponible au catalogue</label>
          </div>
          <button 
            type="submit" 
            className="btn-primary w-full py-3 font-bold mt-4"
            disabled={saveMutation.isPending}
          >
            {saveMutation.isPending ? "Enregistrement..." : editingEq ? "Mettre à jour" : "Créer l'équipement"}
          </button>
        </form>
      </Modal>
    </div>
  );
}
