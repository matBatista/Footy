using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Models.Model
{
    public class FundamentoDetalhado
    {
        public int Id { get; set; }
        public string Nome { get; set; }
        public FundamentoDetalhe Errados { get; set; }
        public FundamentoDetalhe Certos { get; set; }
        public FundamentoDetalhe Totais { get; set; }
    }
}
