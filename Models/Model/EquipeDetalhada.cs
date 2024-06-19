using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Models.Model
{
    public class FundamentoEquipe
    {
        public int id { get; set; }
        public string nome { get; set; }
        public double? qtdJogos { get; set; }
        public ValoresFundamento certos { get; set; }
        public ValoresFundamento errados { get; set; }
        public ValoresFundamento totais { get; set; }
    }
    public class EquipeDetalhada
    {
        public int Id { get; set; }
        public string NomeEquipe { get; set; }
        public double? QtdJogos { get; set; }
        public string SrcLogo { get; set; }

        public List<FundamentoEquipe> FundamentosPros { get; set; }
        public List<FundamentoEquipe> FundamentosContra { get; set; }

        public EquipeDetalhada(FundamentoGeral equipeDetalhe)
        {
            Id = equipeDetalhe.id;
            NomeEquipe = equipeDetalhe.nomeEquipe;
            QtdJogos = equipeDetalhe.qtdJogos;
            SrcLogo = equipeDetalhe.srcLogo;

            FundamentosPros = new List<FundamentoEquipe>();
            FundamentosContra = new List<FundamentoEquipe>();
        }
    }
}
