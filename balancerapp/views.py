from django.shortcuts import render, redirect
import random
import os
import numpy as np
import random
from itertools import combinations, permutations







def balancer_view(request):

    if 'number_teams_cookie' not in request.session:
        request.session['number_teams_cookie'] = []
    if 'number_teams_cookie' not in request.session:
        request.session['number_teams_cookie'] = np.array([])
    

    if request.method == 'POST':
    
    
        if 'button_111' in request.POST:
            number_teams = request.POST['select_number']
            number_teams_cookie = number_teams
            count_players = int(number_teams) * 5
            numbers_players = range(count_players)
            return render(request, 'index.html', {'number_teams': number_teams, 'numbers_players': numbers_players,})
            
            
        elif 'button_222' in request.POST:
            post_dict = request.POST
            post_dict = post_dict.dict() #переводим django QueryDict в обычный питоновский словарь
            post_dict.pop('csrfmiddlewaretoken') #удаляем из словаря лишние строки (первую csrfmiddlewaretoken и последнюю button_222)
            post_dict.pop('button_222')            #чтоб остались только ники и рейтинги игроков
            
            #находим список имен игроков, для этого из словаря post_dict извлекаем каждое четвертое значение
            name_list = []
            j = 0
            for i in post_dict.values():
                if j == 0:
                    name_list.append(i)
                j+=1
                if j==4:
                    j=0
            
            #находим одномерный numpy массив, для этого из словаря post_dict извлекаем каждое 2,3 и 4 значение
            rate_array=np.array([])
            j = 0
            for i in post_dict.values():
                if j == 0:
                    j+=1
                    continue
                j+=1
                rate_array = np.append(rate_array, int(i))
                
                if j==4:
                    j=0
            rate_array = rate_array.reshape(-1,3)#меняем размерность массива так чтоб было три столбца, а количество строк рассчиталось автоматически (-1)
            
            
            #-----------------------подключаем сам балансировщик-------------------
            
            teams = int(len(name_list) / 5) #находим количество команд так, потому что лень пробрасывать значение переменной из одного if в другой if
            max_dispersion = 3 #максимально допустимый разброс между суммарными рейтингами команд
            rates = rate_array #двумерный numpy массив с 3 столбцами (танк, дд, хил) с рейтингами игроков, каждая строчка это игрок
            
            #teams_num - двумерный numpy массив с 5 столбцами (танк, дд, дд, хил, хил) с номерами игроков в каждой команде
            #teams_rates - двумерный numpy массив с 5 столбцами (танк, дд, дд, хил, хил) с рейтингами игроков в каждой команде
            #sum_team_rates - одномерный numpy массив с суммарными рейтингами команд
            try:
                teams_num,teams_rates,sum_team_rates = team_balancer(teams, max_dispersion, rates)
            except:
                pass
            else:
                success = True
            
            #----------------------------------------------------------------------
            
            matrix=[]
            for i in range(teams):
                one_team_list = []
                one_team_list_plus_sumrate = []
                for j in range(5):
                    one_player = []#список из двух значений имя, рейтинг
                    number = teams_num[i][j]
                    name = name_list[int(number)]
                    rate = teams_rates[i][j]
                    rate_str = str(int(rate))
                    one_player.append(name)
                    one_player.append(rate_str)
                    one_team_list.append(one_player)
                one_team_list_plus_sumrate.append(one_team_list)
                one_team_list_plus_sumrate.append(str(int(sum_team_rates[i])))
                matrix.append(one_team_list_plus_sumrate)#трехмерный список команд - в командах игроки и суммарный рейтинг, в игроках имя и рейтинг
            
            
            return render(request, 'index.html', {'success': success, 'teams_num': teams_num, 'teams_rates': teams_rates, 'sum_team_rates': sum_team_rates, 'matrix': matrix})
            
            
            
        else:
            pass
            
    else:
        folder = 'static/img/zen/'
        files = os.listdir(folder)
        zenyatta = random.choice(files)
              
        return render(request, 'index.html', {'zenyatta': zenyatta,})











def team_balancer(teams, max_dispersion, rates):
    #teams = 8 #число команд
    players = teams * 5 #число игроков
    #max_dispersion = 4 #максимальная допустимая разница рейтингов команд

    #количество закрытых ролей (неиграющих ролей) и общая сумма всех рейтингов
    count_zero = 0
    sum_all_rates = 0
    for i in range(players):
        for j in range(3):
            if rates[i,j] == 0:
                count_zero+=1
            else:
                sum_all_rates+= rates[i,j]
    print(count_zero)
    print(sum_all_rates)


    #количество играющих ролей (не нулевой рейт) и средний рейт
    count_not_zero = (len(rates) * 3) - count_zero
    avg_rate = sum_all_rates / count_not_zero
    print(count_not_zero)
    print(avg_rate)


    only_tank = []#список номеров игроков только с ролью только танк
    only_dps = []#только дпс
    only_heal = []#
    tank_and_dps = []
    tank_and_heal = []
    dps_and_heal = []
    universal = []#игроки у которых все три роли открыты
    for i in range(players):
        if rates[i,0] != 0 and rates[i,1] == 0 and rates[i,2] == 0:
            only_tank.append(i)
        elif rates[i,0] == 0 and rates[i,1] != 0 and rates[i,2] == 0:
            only_dps.append(i)
        elif rates[i,0] == 0 and rates[i,1] == 0 and rates[i,2] != 0:
            only_heal.append(i)
        elif rates[i,0] == 0 and rates[i,1] != 0 and rates[i,2] != 0:
            dps_and_heal.append(i)
        elif rates[i,0] != 0 and rates[i,1] != 0 and rates[i,2] == 0:
            tank_and_dps.append(i)
        elif rates[i,0] != 0 and rates[i,1] == 0 and rates[i,2] != 0:
            tank_and_heal.append(i)
        elif rates[i,0] != 0 and rates[i,1] != 0 and rates[i,2] != 0:
            universal.append(i)
        else:
            pass
    print(only_tank)
    print(only_dps)
    print(only_heal)
    print(tank_and_dps)
    print(tank_and_heal)
    print(dps_and_heal)
    print(universal)

    #массив в котором будут команды (по строкам), значения - номера игроков
    teams_num = np.zeros((teams,5))
    #массив в котором будут команды (по строкам), значения - рейтинги игроков
    teams_rates = np.zeros((teams,5))

    #список из которого будум убирать игроков если их распределили 
    box = list(range(0,players))
    print(box)


    #скольо нехватает танков если брать из only_tank (сколкьо нужно добрать из тех, у кого роль не только танк)
    deficit_tank = teams - len(only_tank)
    deficit_dps = teams * 2 - len(only_dps)
    deficit_heal = teams * 2 - len(only_heal)
    print(deficit_tank)
    print(deficit_dps)
    print(deficit_heal)


    #box_tank список игроков у которых 2 или 3 роли и есть танк в роли
    box_tank = tank_and_dps + tank_and_heal + universal
    i = 0
    #расставляем онлитанков в команды
    if len(only_tank) != 0:
        for j in only_tank:
            teams_num[i,0] = j
            teams_rates[i,0] = rates[j,0]
            box.remove(j)#удаляем из списка карзина
            i+=1

    else:
        pass

    i = 0 
    #выбраем рандомно из box_tank и назначаем в команды в которых не хватило танка
    for j in teams_num:
        if i in range(len(only_tank)):
            i+=1
            continue #пропускам команды в которых уже назначены танки из only_tanks
        else:
            pass
        if teams_num[i,0] == 0 :
            r = random.choice(box_tank)
            teams_num[i,0] = r
            teams_rates[i,0] = rates[r,0]
            box.remove(r)
            if r in tank_and_dps:
                tank_and_dps.remove(r)
            elif r in tank_and_heal:
                tank_and_heal.remove(r)
            else:
                universal.remove(r)
        else:
            pass
        i+=1
        
    print(teams_num)
    print(teams_rates)
    print(box)



    #переменная чтоб посчитать сколько комбинаций команд всего существует
    count_combinations = 0
    #переменная чтоб посчитать сколько комбинаций команд всего существует вместе с перестановками
    count_permutations = 0
    #количество хороших команд (у которых сошлись роли)
    count_good = 0

    role=np.array([1,1,2,2])

    #xxx = list(range(0, 40)) #список номеров игроков от 0 до 39
    xxx = box
    #good_combo массив в который запишем все хорошие комбинации ддхх
    good_combo = np.array([0,0,0,0])
    #good_combo = []
     
    #комбинации по четыре из всех нераспределенных игроков
    for i in combinations(xxx, 4):
        count_combinations+=1
        for j in permutations(i):
            count_permutations+=1
            good_combination = True #переменная означает можно ли собрать команду из такого состава
            sum_rate = 0 #переменная для суммы рейтинга команды
            avg_rate = 0 #переменная для среднего рейтинга команды
            #проверяем игроков, не равен ли их рейтинг нулю на назначенной роли
            for k in range(4):
                player = j[k]
                role_1 = role[k]
                if rates[player][role_1] == 0:
                    good_combination = False
                    sum_rate = 0
                    avg_rate = 0
                    break
                else:
                    sum_rate = sum_rate + rates[player][role_1]
            if good_combination == False:
                continue
                    #continue как вreak, только не завершает цикл а прерывает его текущую итерацию
            else:    
                avg_rate = sum_rate / 4
                count_good+=1
                good_combo = np.vstack([good_combo, j])
                
    print('------------------')           
    print(count_combinations)
    print(count_permutations)
    print(count_good)
    print(good_combo)
    
    
    #удаляем первую строку с нулями которую мы записали при инициализации массива
    good_combo = np.delete(good_combo,(0), axis = 0)
    print(good_combo)
    
    
    #каждая 2,3 и 4 строка избыточна, так как это просто перестановки первой, поэтому в массив good_combo2 собтираем каждую четвертую строку

    good_combo2 = np.array([0,0,0,0])

    for j in range(0,len(good_combo), 4):
        i = good_combo[j]
        good_combo2 = np.vstack([good_combo2, i])
    #удаляем первую строку с нулями которую записали при инициализации массива
    good_combo2 = np.delete(good_combo2,(0), axis = 0)
    print(good_combo2)


    #средний рейтинг распределенных танков
    sum_t = teams_rates.sum(axis = 0)
    avg_t = sum_t[0]/teams
    print(avg_t)


    #массив с рейтингами в хороших комбинациях
    dh_rates = np.array([0,0,0,0])

    for i in range(len(good_combo2)):
        list_p = []
        for j in range(4):
            player = good_combo2[i][j]
            rate = 0
            if j < 2:
                rate = rates[player][1]
            else:
                rate = rates[player][2]
            list_p.append(rate)   
        
        dh_rates = np.vstack([dh_rates, list_p])   
    dh_rates = np.delete(dh_rates,(0), axis = 0)
    print(dh_rates)


    #массив из суммарных рейтингов комбинаций
    sum_dh = dh_rates.sum(axis = 1)
    #sum_dh.transpose()
    print(sum_dh)
    #средний рейтинг комбинаций
    avg_dh = np.mean(sum_dh)
    print(avg_dh)


    #округленная сумма среднего рейтинга танков и среднего рейтинга комбинаций
    avg_team = round(avg_t + avg_dh)
    print(avg_team)

    #список суммарных рейтингов ддхх которые нужно подобрать в команды, чтоб баланс сошелся к avg_team
    deficite_dh = []
    for i in range(teams):
        deficite = avg_team - teams_rates[i][0]
        deficite_dh.append(deficite)
    print(deficite_dh)


    #подбираем из списка "хороших" распределений ДДХХ (в которых сошлись роли) возможные комбинации полного распределения игроков
    for k in range(10000):
        list_success = [] #список успешного полного распределения (когда все игроки задействованы) 
        good_combo3 = good_combo2
        dispersion = 9999 #отклонение отдельной команды
        for i in range(teams):
            try:
                r = random.choice(good_combo3) #в каждую команду рандомно подбираем "хорошее" ДДХХ
                list_success.append(r)
                for j in r:
                    for_delete = np.where(np.any(good_combo3==j, axis=1))#for_delete - номера строк где хотябы один элимент равен j 
                    good_combo3 = np.delete(good_combo3,(for_delete), axis = 0) #убираем из списка "хороших" ДДХХ те распределения в которых есть игроко которые уже попали в команду, чтоб они не попадали еще раз
            except:
                break
        if len(list_success) == teams: #если полное распределение сошлось (все команды заполнены уникальными играками)
            zzz_rates = np.array([]) #массив рейтингов ДДХХ всех команд
            
            for a in list_success: #выясняем рейтинги всех ДДХХ и записываем в zzz_rates
                list_p = []
                for b in range(4):
                    player = a[b]
                    rate = 0
                    if b < 2:
                        rate = rates[player][1]
                        list_p.append(rate)
                    else:
                        rate = rates[player][2]
                        list_p.append(rate)   
        
                zzz_rates = np.append(zzz_rates, list_p, axis=0)  
                
            zzz_rates = zzz_rates.reshape(teams,4) #переводим из одномерного массива в двумерный с 4 стобцами и строками по количеству команд

            
            zzz_sum = zzz_rates.sum(axis = 1) #массив сумм рейтингов ДДХХ

         
            #--------проверяем дисперсию найденных команд
            tanks = teams_rates[:,0]

            tanks_sort = np.sort(tanks)#отсортировали рейтинги танков по возростанию
            zzz_sum_sort = np.sort(zzz_sum)
            zzz_sum_sort[::-1].sort()#отсортировали суммарные рейтинги подборок ddhh по убыванию 

            check_dispersion = tanks_sort + zzz_sum_sort
            check_dispersion.sort()

            dispersion = check_dispersion[-1] - check_dispersion[0]
      
        if dispersion <= max_dispersion: #если разброс рейтингов команд меньше или равен максимально допустимому то выходим из цикла (мы нашли что искали)
            print(tanks)
            print(tanks_sort)
            print('---')
            print(zzz_sum)
            print(zzz_sum_sort)
            print('---')
            print(check_dispersion)
            print('YES!!! dispersion: ' + str(dispersion))
            break
        else:
            continue
        #-------------------------------------------
        
    print(avg_team)    


    print(teams_num)
    print('+++')
    print(teams_rates)
    print('--------')

    print('deficite_dh:')
    print(deficite_dh)
    print('zzz_sum:')
    print(zzz_sum)
    print('-----')
    array_deficite_dh = np.array(deficite_dh)#deficite_dh у нас список, поэтому переводим в массив чтоб далее отсортировать как массив

    sorted_idx_zzz_sum = zzz_sum.argsort()#возвращает массив индексов массива zzz_sum в порядке возростания значений элементов zzz_sum
    sorted_idx_deficite_dh = array_deficite_dh.argsort()#сортируем по возрастанию значения массива array_deficite_dh и возвращаем массив индексов

    print('sorted_idx_deficite_dh:')
    print(sorted_idx_deficite_dh)

    print('sorted_idx_zzz_sum:')
    print(sorted_idx_zzz_sum)
    print('----------')


    #заполняем массивы teams_num (массив номеров игроков) и teams_rates (массив рейтингов игроков)
    #таким образом чтоб ДДХХ c наибольшим суммарным рейтингом попал в команду к самому слабому танку и наоборот, чтоб команды сбалансировались 

    for i in range(teams):
        team_num = sorted_idx_deficite_dh[i]
        ddhh_num = sorted_idx_zzz_sum[i]
        ddhh = list_success[ddhh_num]
        list_rates = zzz_rates[ddhh_num]
        print(i)
        print(team_num)
        print(ddhh)
        print(list_rates)
        print('----')
        for j in range(4):
            teams_num[team_num][j+1] = ddhh[j]
            teams_rates[team_num][j+1] = list_rates[j]


    print(teams_num)
    print(teams_rates)

    #проверяем еще раз что у нас команды получились сбалансированые
    sum_team_rates = teams_rates.sum(axis = 1)
    print(sum_team_rates)

    return(teams_num,teams_rates,sum_team_rates)












