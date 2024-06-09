using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Models.Model
{
    public class ObjectFundamentoPartida
    {
        public List<FundamentoPartida> fundamentos { get; set; }
    }
    public class FundamentoPartida
    {
        public int idFundamento { get; set; }
        public string nome { get; set; }
        public EquipePartida mandante { get; set; }
        public EquipePartida visitante { get; set; }
    }

    public class EquipePartida
    {
        public List<Jogador> jogoCompleto { get; set; }
        public List<Jogador> primeiroTempo { get; set; }
        public List<Jogador> segundoTempo { get; set; }
    }

    public class Jogador
    {
        public string nomeJogador { get; set; }
        public int acoesCertas { get; set; }
        public int acoesErradas { get; set; }
    }
}
