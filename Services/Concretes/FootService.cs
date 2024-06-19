using Services.Interfaces;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;
using Models;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json;
using static System.Runtime.InteropServices.JavaScript.JSType;
using Models.Model;

namespace Services.Concretes
{
    public class FootService : BaseService, IFootService
    {
        public IConfiguration _configuration;

        public FootService(IConfiguration configuration) : base (configuration)
        {
            _configuration = configuration;
        }

        public async Task<ObjectCampeonato> RetornaCampeonatos()
        {

            ObjectCampeonato result = new ObjectCampeonato();

            HttpClient client = new HttpClient();

            client = GetHttpClient();

            HttpResponseMessage response = await client.GetAsync(this.footstats_url + "campeonatos");

            if (response.IsSuccessStatusCode)
            {
                string responseBody = await response.Content.ReadAsStringAsync();

                try
                {
                    var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(responseBody);

                    result = JsonConvert.DeserializeObject<ObjectCampeonato>(data["data"].ToString());
                }
                catch (Exception ex)
                {

                }
            }

            ObjectCampeonato obj = new ObjectCampeonato();
            obj.categorias = new List<Categoria>();

            foreach (var res in result.categorias)
            {
                Categoria nova = new Categoria();
                nova.categoria = res.categoria;
                nova.campeonatos = new List<Campeonato>();
                foreach (var camp in res.campeonatos)
                {
                    if (camp.nome.Contains("24"))
                    {

                        ObjectRodadas rodadas = await RetornaRodadasCampeonato(camp.id);
                        
                        if (rodadas.rodadas.SelectMany(x => x.partidas).Any(p => p.dataHora >= DateTime.Now))
                        {
                            nova.campeonatos.Add(camp);
                        }
                    }
                }

                obj.categorias.Add(nova);

            }

            return obj;
        }
        public async Task<ObjectRodadas> RetornaRodadasCampeonato(int id_campeonato)
        {

            //string footstats_url = _configuration["footstats_url"];

            ObjectRodadas result = new ObjectRodadas();

            HttpClient client = new HttpClient();

            client = GetHttpClient();

            HttpResponseMessage response = await client.GetAsync(this.footstats_url + $"campeonatos/{id_campeonato}/calendario");

            if (response.IsSuccessStatusCode)
            {
                string responseBody = await response.Content.ReadAsStringAsync();

                try
                {
                    var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(responseBody);

                    result = JsonConvert.DeserializeObject<ObjectRodadas>(data["data"].ToString());

                    //data = JsonConvert.DeserializeObject<ObjetoCategoria>(responseBody);
                }
                catch (Exception ex)
                {

                }
            }
            else
            {
                //data.info_error = $"Failed to retrieve data. Status code: {response.StatusCode}";
            }

            return result;
        }
        public async Task<ObjectFundamentoPartida> RetornaFundamentos(int id_partida)
        {
            //string footstats_url = _configuration["footstats_url"];

            ObjectFundamentoPartida result = new ObjectFundamentoPartida();

            HttpClient client = new HttpClient();

            client = GetHttpClient();

            HttpResponseMessage response = await client.GetAsync(this.footstats_url + $"partidas/v2/{id_partida}/fundamento");

            if (response.IsSuccessStatusCode)
            {
                string responseBody = await response.Content.ReadAsStringAsync();

                try
                {
                    var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(responseBody);

                    result = JsonConvert.DeserializeObject<ObjectFundamentoPartida>(data["data"].ToString());

                    //data = JsonConvert.DeserializeObject<ObjetoCategoria>(responseBody);
                }
                catch (Exception ex)
                {

                }
            }
            else
            {
                //data.info_error = $"Failed to retrieve data. Status code: {response.StatusCode}";
            }

            return result;
        }

        public async Task<ObjectFundamentoGeral> RetornaRankingFundamentos(int id_campeonato)
        {
            //string footstats_url = _configuration["footstats_url"];

            ObjectFundamentoGeral result = new ObjectFundamentoGeral();

            HttpClient client = new HttpClient();

            client = GetHttpClient();

            HttpResponseMessage response = await client.GetAsync(this.footstats_url + $"campeonatos/{id_campeonato}/equipes/ranking");

            if (response.IsSuccessStatusCode)
            {
                string responseBody = await response.Content.ReadAsStringAsync();

                try
                {
                    var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(responseBody);

                    result = JsonConvert.DeserializeObject<ObjectFundamentoGeral>(data["data"].ToString());
                }
                catch (Exception ex)
                {

                }
            }
            else
            {
                //data.info_error = $"Failed to retrieve data. Status code: {response.StatusCode}";
            }

            return result;
        }

        public async Task<ObjectFundamentoJogador> RetornaFundamentoJogador(int id_campeonato, int id_fundamento)
        {
            //string footstats_url = _configuration["footstats_url"];

            ObjectFundamentoJogador result = new ObjectFundamentoJogador();

            HttpClient client = new HttpClient();

            client = GetHttpClient();

            HttpResponseMessage response = await client.GetAsync(this.footstats_url + $"campeonatos/{id_campeonato}/fundamento/{id_fundamento}/jogadores/ranking");

            if (response.IsSuccessStatusCode)
            {
                string responseBody = await response.Content.ReadAsStringAsync();

                try
                {
                    var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(responseBody);

                    result = JsonConvert.DeserializeObject<ObjectFundamentoJogador>(data["data"].ToString());
                }
                catch (Exception ex)
                {

                }
            }
            else
            {
                //data.info_error = $"Failed to retrieve data. Status code: {response.StatusCode}";
            }

            return result;
        }
        
        public async Task<ObjectEscalacaoPartida> RetornaEscalacao(int id_partida)
        {
            //string footstats_url = _configuration["footstats_url"];

            ObjectEscalacaoPartida result = new ObjectEscalacaoPartida();

            HttpClient client = new HttpClient();

            client = GetHttpClient();

            HttpResponseMessage response = await client.GetAsync(this.footstats_url + $"/partidas/{id_partida}/escalacao");

            if (response.IsSuccessStatusCode)
            {
                string responseBody = await response.Content.ReadAsStringAsync();

                try
                {
                    var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(responseBody);

                    result = JsonConvert.DeserializeObject<ObjectEscalacaoPartida>(data["data"].ToString());

                    //data = JsonConvert.DeserializeObject<ObjetoCategoria>(responseBody);
                }
                catch (Exception ex)
                {

                }
            }
            else
            {
                //data.info_error = $"Failed to retrieve data. Status code: {response.StatusCode}";
            }

            return result;
        }

        //public async Task<ObjectEscalacaoPartida> RetornaEscalacaoPartida(int id_partida)
        //{
        //    //string footstats_url = _configuration["footstats_url"];

        //    ObjectEscalacaoPartida result = await RetornaEscalacao(id_partida);

        //}


        public async Task<List<FundamentoStats>> RetornaFundamentosEquipe(int id_campeonato, int id_equipe)
        {
            ObjectFundamentoGeral list = await RetornaRankingFundamentos(id_campeonato);

            List<FundamentoStats> listStatus = new List<FundamentoStats>();
            
            UpdateFundamentoStatus(list.pros, listStatus, id_equipe, true);
            UpdateFundamentoStatus(list.contra, listStatus, id_equipe, false);

            return listStatus;
        }
        private void UpdateFundamentoStatus(List<FundamentosGeral> fundamentos, List<FundamentoStats> listStatus, int id_equipe, bool isPro)
        {
            foreach (var fundamento in fundamentos)
            {
                if (fundamento.nome == "Índice") continue;

                var detalhe = fundamento.equipes.FirstOrDefault(x => x.id == id_equipe);
                if (detalhe == null) continue;

                var existingStatus = listStatus.FirstOrDefault(x => x.nome == fundamento.nome);

                if (existingStatus == null)
                {
                    FundamentoStats newStatus = new FundamentoStats
                    {
                        nome = fundamento.nome,
                        qtdJogos = detalhe.qtdJogos
                    };

                    UpdateStatus(newStatus, detalhe, isPro);
                    listStatus.Add(newStatus);
                }
                else
                {
                    UpdateStatus(existingStatus, detalhe, isPro);
                }
            }
        }

        private void UpdateStatus(FundamentoStats status, FundamentoGeral detalhe, bool isPro)
        {
            if (isPro)
            {
                status.pros_certos = detalhe.certos?.total;
                status.pros_errados = detalhe.errados?.total;
                status.pros_total = detalhe.totais?.total;
                status.pros_media = detalhe.totais?.media;
            }
            else
            {
                status.cons_certos = detalhe.certos?.total;
                status.cons_errados = detalhe.errados?.total;
                status.cons_total = detalhe.totais?.total;
                status.cons_media = detalhe.totais?.media;
            }
        }


    }
}
