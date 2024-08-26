import React, { useState, useEffect } from 'react';
import { View, StyleSheet, TouchableOpacity, SafeAreaView, StatusBar } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import CalendarView from '@/components/views/CalendarView';
import HabitView from '@/components/views/HabitView';
import EditView from '@/components/views/EditView';

interface Habit {
  id: string;
  name: string;
  description: string;
}

type HabitLogs = {
  [date: string]: {
    [habitId: string]: boolean;
  };
};

const defaultData: { habits: Habit[], habitLogs: HabitLogs } = {
  habits: [
    {
      id: "1",
      name: "Drink water",
      description: "Drink 8 glasses of water daily"
    },
    {
      id: "2",
      name: "Exercise",
      description: "30 minutes of physical activity"
    },
    {
      id: "3",
      name: "Read",
      description: "Read for 20 minutes before bed"
    }
  ],
  habitLogs: {
    "2024-08-23": {
      "1": true,
      "2": false,
      "3": true
    },
    "2024-08-24": {
      "1": true,
      "2": true,
      "3": false
    },
    "2024-08-25": {
      "1": false,
      "2": true,
      "3": true
    }
  }
};

export default function App() {
  const [habits, setHabits] = useState<Habit[]>(defaultData.habits);
  const [habitLogs, setHabitLogs] = useState<HabitLogs>(defaultData.habitLogs);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [editingHabit, setEditingHabit] = useState<Habit | undefined>(undefined);

  useEffect(() => {
    const loadData = async () => {
      try {
        const storedHabits = await AsyncStorage.getItem('habits');
        const storedLogs = await AsyncStorage.getItem('habitLogs');
        
        if (storedHabits && storedLogs) {
          setHabits(JSON.parse(storedHabits));
          setHabitLogs(JSON.parse(storedLogs));
        } else {
          await AsyncStorage.setItem('habits', JSON.stringify(defaultData.habits));
          await AsyncStorage.setItem('habitLogs', JSON.stringify(defaultData.habitLogs));
        }
      } catch (error) {
        console.error('Error loading data:', error);
      }
    };

    loadData();
  }, []);

  const handleToggleHabit = (habitId: string) => {
    const dateKey = selectedDate.toISOString().split('T')[0];
    setHabitLogs(prevLogs => {
      const updatedLogs = { ...prevLogs };
      if (!updatedLogs[dateKey]) {
        updatedLogs[dateKey] = {};
      }
      updatedLogs[dateKey] = {
        ...updatedLogs[dateKey],
        [habitId]: !updatedLogs[dateKey][habitId]
      };
      AsyncStorage.setItem('habitLogs', JSON.stringify(updatedLogs)).catch(error => 
        console.error('Error saving habit logs:', error)
      );
      return updatedLogs;
    });
  };

  const handleEditHabit = (habit: Habit) => {
    setEditingHabit(habit);
    setEditModalVisible(true);
  };

  const handleAddHabit = () => {
    setEditingHabit(undefined);
    setEditModalVisible(true);
  };

  const handleSaveHabit = (savedHabit: Habit) => {
    setHabits(prevHabits => {
      const newHabits = editingHabit
        ? prevHabits.map(h => h.id === savedHabit.id ? savedHabit : h)
        : [...prevHabits, savedHabit];
      AsyncStorage.setItem('habits', JSON.stringify(newHabits)).catch(error => 
        console.error('Error saving habits:', error)
      );
      return newHabits;
    });
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" backgroundColor="#f0f8ff" />
      <View style={styles.container}>
        <CalendarView selectedDate={selectedDate} onSelectDate={setSelectedDate} />
        <HabitView 
          habits={habits}
          habitLogs={habitLogs}
          selectedDate={selectedDate}
          onToggleHabit={handleToggleHabit}
          onEditHabit={handleEditHabit}
        />
        <TouchableOpacity style={styles.addButton} onPress={handleAddHabit}>
          <Ionicons name="add" size={30} color="white" />
        </TouchableOpacity>
      </View>
      <EditView
        visible={editModalVisible}
        onClose={() => setEditModalVisible(false)}
        onSave={handleSaveHabit}
        habit={editingHabit}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#f0f8ff',
  },
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  addButton: {
    position: 'absolute',
    right: 20,
    bottom: 20,
    backgroundColor: '#4a90e2',
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
});