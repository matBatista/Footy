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
        
        public async Task<ObjectEscalacaoPartida> getRetornoPartidaEscalacao(int id_partida)
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

        public async Task<List<EscalcaoPartida>> RetornaEscalacaoPartida(int id_partida)
        {
            //string footstats_url = _configuration["footstats_url"];
            List<EscalcaoPartida> list = new List<EscalcaoPartida>();

            ObjectEscalacaoPartida result = await getRetornoPartidaEscalacao(id_partida);


            int x = 0;
            while( x < 11)
            {
                EscalcaoPartida escalacao = new EscalcaoPartida();
                var v = result.Titular.Visitante[x];
                var m = result.Titular.Mandante[x];

                JogadorView vm = new JogadorView
                {
                    pos = v.Posicao,
                    gols = v.Gols,
                    cartao = v.CartaoAmarelo ? 1 : 0,
                    cartao_vermelho = v.CartaoVermelho ? 1 : 0,
                    gols_contra = v.GolsContra,
                    nome = v.NomeJogador,
                    numero = v.NumeroDaCamisa,
                    sub = v.FoiSubstituido == null ? null : new JogadorView
                    {
                        pos = v.FoiSubstituido.Posicao,
                        gols = v.FoiSubstituido.Gols,
                        cartao = v.FoiSubstituido.CartaoAmarelo ? 1 : 0,
                        cartao_vermelho = v.FoiSubstituido.CartaoVermelho ? 1 : 0,
                        gols_contra = v.FoiSubstituido.GolsContra,
                        nome = v.FoiSubstituido.NomeJogador,
                        numero = v.FoiSubstituido.NumeroDaCamisa,
                        sub = null
                    }
                };
                JogadorView mm = new JogadorView
                {
                    pos = m.Posicao,
                    gols = m.Gols,
                    cartao = m.CartaoAmarelo ? 1 : 0,
                    cartao_vermelho = m.CartaoVermelho ? 1 : 0,
                    gols_contra = m.GolsContra,
                    nome = m.NomeJogador,
                    numero = m.NumeroDaCamisa,
                    sub = m.FoiSubstituido == null ? null : new JogadorView
                    {
                        pos = m.FoiSubstituido.Posicao,
                        gols = m.FoiSubstituido.Gols,
                        cartao = m.FoiSubstituido.CartaoAmarelo ? 1 : 0,
                        cartao_vermelho = m.FoiSubstituido.CartaoVermelho ? 1 : 0,
                        gols_contra = m.FoiSubstituido.GolsContra,
                        nome = m.FoiSubstituido.NomeJogador,
                        numero = m.FoiSubstituido.NumeroDaCamisa,
                        sub = null
                    }
                };

                escalacao.visitante = vm;
                escalacao.mandante = mm;

                list.Add(escalacao);

                x++;
            }

            return list;

        }

        public async Task<List<Estatistica>> RetornaEstatisticas(int id_campeonato, int id_equipe_a, int id_equipe_b)
        {
            ObjectFundamentoGeral list = await RetornaRankingFundamentos(id_campeonato);

            List<FundamentoStats> list_equipe_a = new List<FundamentoStats>();
            
            UpdateFundamentoStatus(list.pros, list_equipe_a, id_equipe_a, true);
            UpdateFundamentoStatus(list.contra, list_equipe_a, id_equipe_a, false);

            List<FundamentoStats> list_equipe_b = new List<FundamentoStats>();

            UpdateFundamentoStatus(list.pros, list_equipe_b, id_equipe_b, true);
            UpdateFundamentoStatus(list.contra, list_equipe_b, id_equipe_b, false);


            List<Estatistica> listStast = new List<Estatistica>();

            int x = 0;
            while(x < list_equipe_a.Count)
            {
                
                FundamentoStats fm = list_equipe_a[x];
                FundamentoStats fv = list_equipe_b[x];

                int o = 0;

                if(fm.nome == "Posse de bola")
                {

                }
                Estatistica stats = new Estatistica
                {
                    nome = fm.nome,
                    mandante = new FundamentoStats
                    {
                        qtdJogos = fm.qtdJogos ?? 0,
                        pros_certos = fm.pros_certos ?? 0,
                        pros_total = fm.pros_total ?? fm.pros_certos ?? 0,
                        pros_media = fm.pros_media ?? ((fm.pros_total ?? fm.pros_certos) / fm.qtdJogos),
                        pros_errados = fm.pros_errados ?? 0,
                        cons_certos = fm.cons_certos ?? 0,
                        cons_errados = fm.cons_errados ?? 0,
                        cons_total = fm.cons_total ?? fm.cons_certos ?? 0,
                        cons_media = fm.cons_media ?? ((fm.cons_total ?? fm.cons_certos)/ fm.qtdJogos),
                        nome = fm.nome
                    },
                    visitante = new FundamentoStats
                    {
                        qtdJogos = fv.qtdJogos ?? 0,
                        pros_certos = fv.pros_certos ?? 0,
                        pros_errados = fv.pros_errados ?? 0,
                        pros_total = fv.pros_total ?? fv.pros_certos ?? 0,
                        pros_media = fv.pros_media ?? ((fv.pros_total ?? fv.pros_certos) / fv.qtdJogos),
                        cons_certos = fv.cons_certos ?? 0,
                        cons_errados = fv.cons_errados ?? 0,
                        cons_total = fv.cons_total ?? fv.cons_certos ?? 0,
                        cons_media = fv.cons_media ?? ((fv.cons_total ?? fv.cons_certos) / fv.qtdJogos),
                        nome = fv.nome
                    }
                };

                listStast.Add(stats);

                x++;
            }

            return listStast;
        }
        private void UpdateFundamentoStatus(List<FundamentosGeral> fundamentos, List<FundamentoStats> listStatus, int id_equipe, bool isPro)
        {
            foreach (var fundamento in fundamentos)
            {
                if (fundamento.nome == "Índice") continue;
                //if (fundamento.nome == "Perda da posse de bola") continue;
                if (fundamento.nome == "Cartões amarelos") continue;
                if (fundamento.nome == "Cartões vermelhos") continue;
                if (fundamento.nome == "Impedimentos") continue;
                if (fundamento.nome == "Rebatidas") continue;
                //if (fundamento.nome == "Assistências para finalização") continue;
                if (fundamento.nome == "Posse de bola") continue;

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
