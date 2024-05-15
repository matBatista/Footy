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

        public async Task<ObjetoCategoria> RetornaCampeonatos()
        {
           
            string footstats_url = _configuration["footstats_url"];

            ObjetoCategoria data = new ObjetoCategoria();

            HttpClient client = new HttpClient();

            client = GetHttpClient();

            HttpResponseMessage response = await client.GetAsync(footstats_url + "campeonatos");

            if (response.IsSuccessStatusCode)
            {
                string responseBody = await response.Content.ReadAsStringAsync();

                try
                {
                    data = JsonConvert.DeserializeObject<ObjetoCategoria>(responseBody);
                }
                catch (Exception ex)
                {

                }
            }
            else
            {
                data.info_error = $"Failed to retrieve data. Status code: {response.StatusCode}";
            }

            return data;
        }
        public async Task<ObjectRodadas> RetornaRodadasCampeonato(int id_campeonato)
        {

            string footstats_url = _configuration["footstats_url"];

            ObjectRodadas rodadas = new ObjectRodadas();

            HttpClient client = new HttpClient();

            client = GetHttpClient();

            HttpResponseMessage response = await client.GetAsync(footstats_url + $"campeonatos/{id_campeonato}/calendario");

            if (response.IsSuccessStatusCode)
            {
                string responseBody = await response.Content.ReadAsStringAsync();

                try
                {
                    var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(responseBody);

                    rodadas = JsonConvert.DeserializeObject<ObjectRodadas>(data["data"].ToString());

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

            return rodadas;
        }
        public async Task<ObjectFundamentos> RetornaFundamentos(int id_partida)
        {
            string footstats_url = _configuration["footstats_url"];

            ObjectFundamentos retorno = new ObjectFundamentos();

            HttpClient client = new HttpClient();

            client = GetHttpClient();

            HttpResponseMessage response = await client.GetAsync(footstats_url + $"partidas/v2/{id_partida}/fundamento");

            if (response.IsSuccessStatusCode)
            {
                string responseBody = await response.Content.ReadAsStringAsync();

                try
                {
                    var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(responseBody);

                    retorno = JsonConvert.DeserializeObject<ObjectFundamentos>(data["data"].ToString());

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

            return retorno;
        }

        public async Task<ObjectRanking> RetornaRankingFundamentos(int id_campeonato)
        {
            string footstats_url = _configuration["footstats_url"];

            ObjectRanking retorno = new ObjectRanking();

            HttpClient client = new HttpClient();

            client = GetHttpClient();

            HttpResponseMessage response = await client.GetAsync(footstats_url + $"campeonatos/{id_campeonato}/equipes/ranking");

            if (response.IsSuccessStatusCode)
            {
                string responseBody = await response.Content.ReadAsStringAsync();

                try
                {
                    var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(responseBody);

                    retorno = JsonConvert.DeserializeObject<ObjectRanking>(data["data"].ToString());

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

            return retorno;
        }


    }
}
