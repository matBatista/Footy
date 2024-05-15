namespace Models { 
    public class Categoria
    {
        public string categoria { get; set; }
        public List<Campeonato> campeonatos { get; set; }
    }

    public class ListaCategorias
    {
        public List<Categoria> categorias { get; set; }
    }

    public class ObjetoCategoria
    {
        public ListaCategorias data { get; set; }
        public object pagination { get; set; }

        public string info_error { get; set; }
    }
}
