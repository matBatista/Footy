import { Routes } from '@angular/router';
import { AppComponent } from './app.component';
import { Component } from '@angular/core';
import { CampeonatoComponent } from './campeonato/campeonato.component';
// import { PartidaComponent } from './partida/partida.component';

export const routes: Routes = [
    {path: 'campeonato/:id_campeonato', component: CampeonatoComponent},
    // {path: 'partida/:id_campeonato/:id_equipe_a/:id_equipe_b', component: PartidaComponent}
];
