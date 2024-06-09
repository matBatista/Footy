import { Routes } from '@angular/router';
import { AppComponent } from './app.component';
import { Component } from '@angular/core';
import { CampeonatoComponent } from './campeonato/campeonato.component';

export const routes: Routes = [
    {path: 'campeonato', component: CampeonatoComponent}
];
