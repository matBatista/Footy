
using System;

namespace Models
{
    public class ObjectCampeonato
    {
        public List <Categoria> categorias { get; set; }
    }
    public class Categoria
    {
        public string categoria { get; set;}   
        public List<Campeonato> campeonatos { get; set;}
    }
    public class ObjectRodadas
    {
      public List<Rodada> rodadas { get; set;}
    }
    public class Campeonato
    {
        public virtual int id { get; set;}
        public virtual string nome { get; set;}
        public virtual string urlLogo { get; set;}
    }
    public class Rodada
    {
        public string fase { get; set; }
        public int? rodada { get; set; }
        public List<PartidaRodada> partidas { get; set; }
        public bool rodadaAtual { get; set; }
    }

    public class PartidaRodada
    {
        public int? id { get; set; }
        public int? idFase { get; set; }
        public EquipeRodada mandante { get; set; }
        public string periodoJogo { get; set; }
        public bool scout { get; set; }
        public EquipeRodada visitante { get; set; }
        public bool temporeal { get; set; }
        public DateTime? dataHora { get; set; }
    }

    public class EquipeRodada
    {
        public int id { get; set; }
        public int? gols { get; set; }
        public string nome { get; set; }
        public string sigla { get; set; }
        public string urlLogo { get; set; }
    }
}
