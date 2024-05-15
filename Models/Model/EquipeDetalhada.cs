using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Models.Model
{
    public class EquipeDetalhada
    {
        public int Id { get; set; }
        public string NomeEquipe { get; set; }
        public int? QtdJogos { get; set; }
        public string SrcLogo { get; set; }

        public List<FundamentoDetalhado> FundamentosPros { get; set; }
        public List<FundamentoDetalhado> FundamentosContra { get; set; }

        public EquipeDetalhada(EquipeDetalhe equipeDetalhe)
        {
            Id = equipeDetalhe.Id;
            NomeEquipe = equipeDetalhe.NomeEquipe;
            QtdJogos = equipeDetalhe.QtdJogos;
            SrcLogo = equipeDetalhe.SrcLogo;

            FundamentosPros = new List<FundamentoDetalhado>();
            FundamentosContra = new List<FundamentoDetalhado>();
        }

        public void AdicionarFundamentosPros(FundamentoTipo fundamento)
        {
            var equipeDetalhe = fundamento.Equipes.FirstOrDefault(e => e.Id == Id);
            if (equipeDetalhe != null)
            {
                FundamentosPros.Add(new FundamentoDetalhado
                {
                    Nome = fundamento.Nome,
                    Errados = equipeDetalhe.Errados,
                    Certos = equipeDetalhe.Certos,
                    Totais = equipeDetalhe.Totais
                });
            }
        }

        public void AdicionarFundamentosContra(FundamentoTipo fundamento)
        {
            var equipeDetalhe = fundamento.Equipes.FirstOrDefault(e => e.Id == Id);
            if (equipeDetalhe != null)
            {
                FundamentosContra.Add(new FundamentoDetalhado
                {
                    Nome = fundamento.Nome,
                    Errados = equipeDetalhe.Errados,
                    Certos = equipeDetalhe.Certos,
                    Totais = equipeDetalhe.Totais
                });
            }
        }
    }

    public class FundamentoDetalhado
    {
        public int Id { get; set; }
        public string Nome { get; set; }
        public FundamentoDetalhe Errados { get; set; }
        public FundamentoDetalhe Certos { get; set; }
        public FundamentoDetalhe Totais { get; set; }
    }
}
