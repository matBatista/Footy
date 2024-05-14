namespace FootAnalises.Model
{
    public class Categoria
    {
        public virtual string categoria { get; set; }
        public virtual List<Campeonato> campeonatos { get; set; }
    }
}
