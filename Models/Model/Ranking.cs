using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Models.Model
{
    public class FundamentoDetalhe
    {
        public double? Media { get; set; }
        public double? Porcentagem { get; set; }
        public int? Total { get; set; }
        public double? TotalFloat { get; set; }
    }

    public class EquipeDetalhe
    {
        public FundamentoDetalhe Certos { get; set; }
        public FundamentoDetalhe Errados { get; set; }
        public int Id { get; set; }
        public string NomeEquipe { get; set; }
        public int? QtdJogos { get; set; }
        public string SrcLogo { get; set; }
        public FundamentoDetalhe Totais { get; set; }
    }

    public class FundamentoTipo
    {
        public List<EquipeDetalhe> Equipes { get; set; }
        public int Id { get; set; }
        public string Nome { get; set; }
    }

    public class ObjectRanking
    {
        public List<FundamentoTipo> Contra { get; set; }
        public List<FundamentoTipo> Pros { get; set; }
    }
}
