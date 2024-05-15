using System;
using System.Collections.Generic;

public class Mandante
{
    public int id { get; set; }
    public object gols { get; set; }
    public string nome { get; set; }
    public string sigla { get; set; }
    public string urlLogo { get; set; }
}

public class Visitante
{
    public int id { get; set; }
    public object gols { get; set; }
    public string nome { get; set; }
    public string sigla { get; set; }
    public string urlLogo { get; set; }
}

public class Partida
{
    public string periodoJogo { get; set; }
    public int idFase { get; set; }
    public Mandante mandante { get; set; }
    public Visitante visitante { get; set; }
    public bool temporeal { get; set; }
    public DateTime? dataHora { get; set; }
    public bool scout { get; set; }
    public int id { get; set; }
}

public class Rodada
{
    public string fase { get; set; }
    public int rodada { get; set; }
    public List<Partida> partidas { get; set; }
    public bool rodadaAtual { get; set; }
}

public class ObjectRodadas
{
    public int intervaloAtualizacaoRodadasEmMilis { get; set; }
    public int intervaloAtualizacaoPartidaEmMilis { get; set; }
    public int intervaloAtualizacaoScoutEmMilis { get; set; }
    public List<Rodada> rodadas { get; set; }
}
