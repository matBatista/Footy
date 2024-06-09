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
            else
            {

            }

            return result;
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


    }
}
