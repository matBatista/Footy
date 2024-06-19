using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;


namespace Models.Model
{
    public class ObjectFundamentoGeral
    {
        public List<FundamentosGeral> contra { get; set; }
        public List<FundamentosGeral> pros { get; set; }
    }
    public class ObjectFundamentoJogador
    {
        public List<FundamentoJogador> fundamentos { get; set; }
    }

    public class FundamentosGeral
    {
        public int id { get; set; }
        public string nome { get; set; }
        public List<FundamentoGeral> equipes { get; set; }
    }
    public class FundamentoGeral
    {
        public int id { get; set; }
        public string nomeEquipe { get; set; }
        public string srcLogo { get; set; }
        public double? qtdJogos { get; set; }
        public ValoresFundamento certos { get; set; }
        public ValoresFundamento errados { get; set; }
        public ValoresFundamento totais { get; set; }
    }
    public class ValoresFundamento
    {
        public double? total { get; set; }
        public double? totalFloat { get; set; }
        public double? media { get; set; }
        public double? porcentagem { get; set; }
    }
    public class FundamentoJogador  
    {
        public int id { get; set; }
        public string nome { get; set; }
        public int idTeam { get; set; }
        public string nomeTime { get; set; }
        public string srcLogo { get; set; }
        public int idJogador { get; set; }
        public string nomeJogador { get; set; }
        public int segundosJogados { get; set; }
        public double? jogos { get; set; }
        public double? total { get; set; }
        public double? totalMedia { get; set; }
        public double? percetual { get; set; }
        public List<ValoresFundamento> detalhes { get; set; }
    }


    public class FundamentoStats
    {
        public string nome { get; set; }
        public double? qtdJogos { get; set; }
        public double? pros_certos { get; set; }
        public double? pros_errados { get; set; }
        public double? pros_total { get; set; }
        public double? pros_media { get; set; }
        public double? cons_certos { get; set; }
        public double? cons_errados { get; set; }
        public double? cons_total { get; set; }
        public double? cons_media { get; set; }

    }

}
