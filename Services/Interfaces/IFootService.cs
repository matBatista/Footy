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
        Task<ObjectCampeonato> RetornaCampeonatos();
        Task<ObjectRodadas> RetornaRodadasCampeonato(int id_campeonato);
        Task<ObjectFundamentoPartida> RetornaFundamentos(int id_partida);
        Task<ObjectFundamentoGeral> RetornaRankingFundamentos(int id_campeonato);
        Task<ObjectFundamentoJogador> RetornaFundamentoJogador(int id_campeonato, int id_fundamento);
        Task<List<Estatistica>> RetornaEstatisticas(int id_campeonato, int id_equipe_a, int id_equipe_b);
        Task<List<EscalcaoPartida>> RetornaEscalacaoPartida(int id_partida);
    }
}
