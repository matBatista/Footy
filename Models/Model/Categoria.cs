namespace Models { 
    public class Categoria
    {
        public string categoria { get; set; }
        public List<Campeonato> campeonatos { get; set; }
    }

    public class Data
    {
        public List<Categoria> categorias { get; set; }
    }

    public class RootObject
    {
        public Data data { get; set; }
        public object pagination { get; set; }
    }
}
