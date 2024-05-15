using System.Collections.Generic;

namespace Models.Model
{
    public class Partida
    {
        public int idPartida { get; set; }
        public Tecnico tecnicoMandante { get; set; }
        public Tecnico tecnicoVisitante { get; set; }
        public Titular titular { get; set; }
        public Reserva reserva { get; set; }
    }

    public class Tecnico
    {
        public string nome { get; set; }
        public bool cartaoAmarelo { get; set; }
        public bool cartaoAmarelo2 { get; set; }
        public bool cartaoVermelho { get; set; }
    }

    public class Jogador
    {
        public int id { get; set; }
        public int idPartida { get; set; }
        public int idEquipe { get; set; }
        public int idJogador { get; set; }
        public string nomeJogador { get; set; }
        public int idPosicao { get; set; }
        public string posicao { get; set; }
        public int numeroDaCamisa { get; set; }
        public bool emCampo { get; set; }
        public object golsInMinutes { get; set; }
        public object indice { get; set; }
        public object ranking { get; set; }
        public bool cartaoAmarelo { get; set; }
        public bool cartaoAmarelo2 { get; set; }
        public bool cartaoVermelho { get; set; }
        public int gols { get; set; }
        public int golsContra { get; set; }
        public Substituicao foiSubstituido { get; set; }
        public bool titular { get; set; }
    }

    public class Titular
    {
        public List<Jogador> mandante { get; set; }
        public List<Jogador> visitante { get; set; }
    }

    public class Reserva
    {
        public List<Jogador> mandante { get; set; }
        public List<Jogador> visitante { get; set; }
    }

    public class Substituicao
    {
        public string nome { get; set; }
        public string tempo { get; set; }
        public string posicao { get; set; }
        public int id { get; set; }
        public int idPartida { get; set; }
        public int idEquipe { get; set; }
        public int idJogador { get; set; }
        public string nomeJogador { get; set; }
        public int idPosicao { get; set; }
        public int numeroDaCamisa { get; set; }
        public bool emCampo { get; set; }
        public bool cartaoAmarelo { get; set; }
        public bool cartaoAmarelo2 { get; set; }
        public bool cartaoVermelho { get; set; }
        public int gols { get; set; }
        public int golsContra { get; set; }
        public object indice { get; set; }
        public object ranking { get; set; }
        public object golsInMinutes { get; set; }
        public bool titular { get; set; }
    }
}
