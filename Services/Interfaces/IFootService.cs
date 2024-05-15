using Models;
using Models.Model;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Services.Interfaces
{
    public interface IFootService
    {
        Task<ObjetoCategoria> RetornaCampeonatos();
        Task<ObjectRodadas> RetornaRodadasCampeonato(int id_campeonato);
        Task<ObjectFundamentos> RetornaFundamentos(int id_partida);
        Task<ObjectRanking> RetornaRankingFundamentos(int id_campeonato);
    }
}
