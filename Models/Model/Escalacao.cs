using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Models.Model
{
    public class ObjectEscalacaoPartida
    {
        public int IdPartida { get; set; }
        public Reserva Reserva { get; set; }
        public Tecnico TecnicoMandante { get; set; }
        public Tecnico TecnicoVisitante { get; set; }
        public Titular Titular { get; set; }
    }

    public class Reserva
    {
        public List<Jogador> Mandante { get; set; }
        public List<Jogador> Visitante { get; set; }
    }

    public class Tecnico
    {
        public bool CartaoAmarelo { get; set; }
        public bool CartaoAmarelo2 { get; set; }
        public bool CartaoVermelho { get; set; }
        public string Nome { get; set; }
    }

    public class Titular
    {
        public List<Jogador> Mandante { get; set; }
        public List<Jogador> Visitante { get; set; }
    }

    public class Jogador
    {
        public bool CartaoAmarelo { get; set; }
        public bool CartaoAmarelo2 { get; set; }
        public bool CartaoVermelho { get; set; }
        public bool EmCampo { get; set; }
        public Substituido FoiSubstituido { get; set; }
        public int Gols { get; set; }
        public int GolsContra { get; set; }
        public List<int> GolsInMinutes { get; set; }
        public int? Id { get; set; }
        public int? IdEquipe { get; set; }
        public int? IdJogador { get; set; }
        public int? IdPartida { get; set; }
        public int? IdPosicao { get; set; }
        public int? Indice { get; set; }
        public string NomeJogador { get; set; }
        public int? NumeroDaCamisa { get; set; }
        public string Posicao { get; set; }
        public int? Ranking { get; set; }
        public bool Titular { get; set; }
        public int? acoesCertas { get; set; }
        public int? acoesErradas { get; set; }
    }

    public class Substituido
    {
        public bool CartaoAmarelo { get; set; }
        public bool CartaoAmarelo2 { get; set; }
        public bool CartaoVermelho { get; set; }
        public bool EmCampo { get; set; }
        public int? Gols { get; set; }
        public int? GolsContra { get; set; }
        public List<int> GolsInMinutes { get; set; }
        public int? Id { get; set; }
        public int? IdEquipe { get; set; }
        public int? IdJogador { get; set; }
        public int? IdPartida { get; set; }
        public int? IdPosicao { get; set; }
        public int? Indice { get; set; }
        public string Nome { get; set; }
        public string NomeJogador { get; set; }
        public int? NumeroDaCamisa { get; set; }
        public string Posicao { get; set; }
        public int? Ranking { get; set; }
        public string Tempo { get; set; }
        public bool Titular { get; set; }
    }
}
