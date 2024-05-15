using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Models.Model
{
    public class JogadorFundamento
    {
        public int? AcoesCertas { get; set; }
        public int? AcoesErradas { get; set; }
        public string NomeJogador { get; set; }
    }

    public class FundamentoEquipe
    {
        public List<JogadorFundamento> JogoCompleto { get; set; }
        public List<JogadorFundamento> PrimeiroTempo { get; set; }
        public List<JogadorFundamento> SegundoTempo { get; set; }
    }

    public class Fundamento
    {
        public int IdFundamento { get; set; }
        public FundamentoEquipe Mandante { get; set; }
        public string Nome { get; set; }
        public FundamentoEquipe Visitante { get; set; }
    }

    public class ObjectFundamentos
    {
        public List<Fundamento> fundamentos { get; set; }
    }

}
